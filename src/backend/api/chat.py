import json
import logging
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Dict, Any, Optional

from src.backend.core.deps import llama_client as llama, vector_store, brain
from src.backend.core.orchestration.validator import validate_narrative_formatting
from src.backend.core.engine.engine import update_needs, evolve_character
from src.backend.db.database import get_db, SessionLocal
from src.backend.db.models import AgentState, Character, User, MessageNode
import re
import uuid
from src.backend.core.config import settings

logger = logging.getLogger(__name__)


def parse_actions_to_state(ai_response: str, state: AgentState):
    """Parses AI response for narrative actions like **enters [location]** and updates state."""
    # Pattern for location: **enters [location]** or **walks into [location]**
    loc_match = re.search(
        r"\*\*(?:enters|walks into|arrives at|is now in) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if loc_match:
        new_loc = loc_match.group(1).strip().strip(".")
        # Strip articles
        new_loc = re.sub(r"^(?:The|A|An)\s+", "", new_loc, flags=re.IGNORECASE)
        new_loc = new_loc.capitalize()
        if new_loc != state.location:
            logger.info(f"State Update: Location -> {new_loc}")
            state.location = new_loc

    # Pattern for outfit: **changes into [outfit]** or **is wearing [outfit]**
    outfit_match = re.search(
        r"\*\*(?:changes into|puts on|is wearing|dresses in) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if outfit_match:
        new_outfit = outfit_match.group(1).strip().strip(".")
        # Strip articles
        new_outfit = re.sub(r"^(?:The|A|An)\s+", "", new_outfit, flags=re.IGNORECASE)
        new_outfit = new_outfit.capitalize()
        if new_outfit != state.clothes:
            logger.info(f"State Update: Clothes -> {new_outfit}")
            state.clothes = new_outfit

    # Physiological stats updates based on keywords in actions
    stats = dict(state.stats) if state.stats else {}

    # Check for eating/drinking
    eat_match = re.search(
        r"\*\*(?:eats|takes a bite of|chews on|drinks|sips|consumes|devours) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if eat_match:
        old_hunger = stats.get("hunger", 0)
        new_hunger = max(0, old_hunger - 30)
        stats["hunger"] = new_hunger
        logger.info(
            f"State Update: Hunger {old_hunger}% -> {new_hunger}% due to eating action"
        )

    # Check for sleeping
    sleep_match = re.search(
        r"\*\*(?:goes to sleep|falls asleep|nods off|sleeps|rests her eyes)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if sleep_match:
        stats["is_sleeping"] = True
        logger.info("State Update: is_sleeping -> True due to sleeping action")

    # Check for waking up
    wake_match = re.search(
        r"\*\*(?:wakes up|stretches and yawns|wakes)\*\*", ai_response, re.IGNORECASE
    )
    if wake_match:
        stats["is_sleeping"] = False
        logger.info("State Update: is_sleeping -> False due to waking action")

    state.stats = stats


router = APIRouter()


async def run_consciousness_layer(
    character_id: int, user_message: str, ai_response: str, force_reflect: bool = False
):
    """Background task for memory and evolution."""
    try:
        db = SessionLocal()
        try:
            # 1. Store memory (always)
            await vector_store.add_memory(
                f"User: {user_message}\nAI: {ai_response}",
                metadata={"character_id": character_id},
            )

            # 2. Reflect & Evolve (only on interval or force)
            if force_reflect:
                # Fetch last 20 messages for deep context
                messages = (
                    db.query(MessageNode)
                    .filter(MessageNode.character_id == character_id)
                    .order_by(MessageNode.timestamp.desc())
                    .limit(20)
                    .all()
                )
                msg_dicts = [
                    {"role": m.role, "content": m.content} for m in reversed(messages)
                ]

                reflection = await brain.reflect(msg_dicts, window_size=20)
                evolve_character(db, character_id, reflection)
                logger.info(
                    f"Consciousness Layer: Reflection complete for character {character_id}"
                )
        finally:
            db.close()
            import gc

            gc.collect()
    except Exception as e:
        logger.exception(f"Consciousness layer error: {e}")


ACTIONS_CONFIG = {
    "hug": {
        "message": "*I step forward and wrap my arms around you in a warm, gentle hug.*",
        "stats": {"happiness": 5, "social": 10, "relationship_score": 2},
    },
    "pat_head": {
        "message": "*I reach out and pat your head gently, smiling softly.*",
        "stats": {"happiness": 3, "social": 5, "relationship_score": 1},
    },
    "tease": {
        "message": "*I look at you with a playful smirk, teasing you lightly.*",
        "stats": {"happiness": 2, "social": 8, "relationship_score": 1},
    },
    "hold_hand": {
        "message": "*I slide my hand into yours, holding it gently.*",
        "stats": {"happiness": 4, "social": 8, "relationship_score": 2},
    },
    "coffee": {
        "message": "*I hand you a hot, freshly brewed cup of black coffee.*",
        "stats": {"hunger": -10, "energy": 15, "relationship_score": 2},
    },
    "croissant": {
        "message": "*I offer you a warm, freshly baked chocolate croissant.*",
        "stats": {"hunger": -35, "energy": 5, "relationship_score": 3},
    },
    "book": {
        "message": "*I present you with a beautifully bound, vintage book.*",
        "stats": {"happiness": 8, "social": 5, "relationship_score": 4},
    },
    "necklace": {
        "message": "*I hand you a small velvet box containing a delicate silver necklace.*",
        "stats": {"happiness": 15, "social": 10, "relationship_score": 8},
    },
}


_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class LLMConfig(BaseModel):
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    preset_id: Optional[int] = None

    @field_validator("base_url")
    @classmethod
    def _base_url_must_be_loopback(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        host = urlparse(v).hostname
        if host not in _LOOPBACK_HOSTS:
            raise ValueError(
                "base_url must point at a loopback address (127.0.0.1/localhost) "
                "— the local llama-server, not an arbitrary remote host"
            )
        return v


class ChatRequest(BaseModel):
    message: Optional[str] = None
    character_id: int = 1
    parent_id: Optional[int] = None
    config: Optional[LLMConfig] = None
    action_id: Optional[str] = None


@router.get("/chat/actions", response_model=Dict[str, str])
async def list_actions():
    """The message text for each quick-action button, single-sourced from
    ACTIONS_CONFIG so the frontend never has to keep its own copy in sync
    (stat deltas stay server-side/internal -- the client only needs the text)."""
    return {action_id: cfg["message"] for action_id, cfg in ACTIONS_CONFIG.items()}


class MessageEditRequest(BaseModel):
    content: str


class ChatResponse(BaseModel):
    reply: str
    request_id: str
    stats: Dict[str, Any] = {}
    latency: Dict[str, float] = {}


class ChatTurnContext:
    """Everything /chat and /chat/stream need after setup, so both routes can
    share one code path instead of re-implementing it (see _prepare_chat_turn)."""

    def __init__(
        self,
        user: User,
        character: Character,
        state: AgentState,
        prompt: str,
        config: "LLMConfig",
        preset_dict: Optional[Dict[str, Any]],
        effective_parent_id: Optional[int],
        user_message_content: Optional[str],
        force_reflect: bool,
    ):
        self.user = user
        self.character = character
        self.state = state
        self.prompt = prompt
        self.config = config
        self.preset_dict = preset_dict
        self.effective_parent_id = effective_parent_id
        self.user_message_content = user_message_content
        self.force_reflect = force_reflect


def _apply_action_stats(
    stats: Optional[Dict[str, Any]], stat_mod: Dict[str, Any]
) -> Dict[str, Any]:
    stats = dict(stats) if stats else {}
    stats["energy"] = max(
        0, min(100, stats.get("energy", 100) + stat_mod.get("energy", 0))
    )
    stats["hunger"] = max(
        0, min(100, stats.get("hunger", 0) + stat_mod.get("hunger", 0))
    )
    stats["happiness"] = max(
        0, min(100, stats.get("happiness", 100) + stat_mod.get("happiness", 0))
    )
    stats["social"] = max(
        0, min(100, stats.get("social", 100) + stat_mod.get("social", 0))
    )

    relationship = stats.get("relationship", {})
    if not isinstance(relationship, dict):
        relationship = {"score": 50}
    old_score = relationship.get("score", 50)
    relationship["score"] = max(
        0, min(100, old_score + stat_mod.get("relationship_score", 0))
    )
    stats["relationship"] = relationship
    return stats


async def _prepare_chat_turn(
    request: ChatRequest, db: Session, request_id: str
) -> ChatTurnContext:
    """Shared setup for /chat and /chat/stream: resolve user/character/state,
    apply action stat deltas, persist the user message, walk history, and
    build the prompt. Raises on failure -- callers decide how to surface it."""
    user = User.get_or_create_active(db)

    character = db.query(Character).filter(
        Character.id == request.character_id
    ).first() or Character.get_default(db)
    state = character.state or AgentState(character_id=character.id)
    if not state.id:
        db.add(state)
        db.flush()

    state.stats = update_needs(state.stats, datetime.now(timezone.utc))
    state.interaction_count += 1
    force_reflect = state.interaction_count % 20 == 0
    # Commit the decay/counter bump now, unconditionally -- a message-less
    # "regenerate" call never reaches the request.message commit below, and
    # this session gets closed (without a commit) once the request ends.
    try:
        db.commit()
    except StaleDataError:
        # A stat-tweak PUT (or another chat turn) already updated this
        # AgentState row -- this is routine same-user rapid-fire usage, not a
        # real multi-writer conflict, so pick up its fresh state instead of
        # failing the whole turn over a redundant decay tick. Re-query rather
        # than db.refresh(state): refresh requires the instance still be
        # attached the way it was before the rollback, which isn't guaranteed.
        db.rollback()
        state = db.query(AgentState).filter(AgentState.id == state.id).first()
        force_reflect = state.interaction_count % 20 == 0

    effective_parent_id = (
        request.parent_id if request.parent_id is not None else state.current_message_id
    )
    user_message_content = request.message

    if request.action_id and request.action_id in ACTIONS_CONFIG:
        action_cfg = ACTIONS_CONFIG[request.action_id]
        user_message_content = action_cfg["message"]
        request.message = user_message_content
        state.stats = _apply_action_stats(state.stats, action_cfg.get("stats", {}))

    if not user_message_content and effective_parent_id:
        last_msg = (
            db.query(MessageNode).filter(MessageNode.id == effective_parent_id).first()
        )
        if last_msg and last_msg.role == "user":
            user_message_content = last_msg.content

    if request.message:
        user_msg = MessageNode(
            character_id=character.id,
            user_id=user.id,
            role="user",
            content=request.message,
            parent_id=effective_parent_id,
            request_id=request_id,
        )
        db.add(user_msg)
        db.flush()
        state.current_message_id = user_msg.id
        try:
            db.commit()
        except StaleDataError:
            # Same routine-contention case as the decay commit above, but a
            # failed commit rolls back the just-flushed user_msg INSERT too --
            # re-add it against the now-fresh state instead of losing the
            # user's message.
            db.rollback()
            state = db.query(AgentState).filter(AgentState.id == state.id).first()
            db.add(user_msg)
            db.flush()
            state.current_message_id = user_msg.id
            db.commit()
        effective_parent_id = user_msg.id

    history = []
    curr_id = effective_parent_id
    while curr_id and len(history) < 50:
        m = (
            db.query(MessageNode)
            .filter(MessageNode.id == curr_id, MessageNode.is_active == True)
            .first()
        )
        if not m:
            break
        history.append({"role": m.role, "content": m.content})
        curr_id = m.parent_id
    history.reverse()

    prompt = await brain.build_prompt(
        user_message_content or "",
        character,
        {
            "location": state.location,
            "mood": state.mood,
            "stats": state.stats,
            "active_summary": getattr(state, "active_summary", ""),
        },
        user=user,
        history=history[:-1] if request.message else history,
        db=db,
    )

    config = request.config or LLMConfig()

    from src.backend.db.models import SamplerPreset

    if config.preset_id:
        preset_obj = (
            db.query(SamplerPreset).filter(SamplerPreset.id == config.preset_id).first()
        )
    else:
        preset_obj = (
            db.query(SamplerPreset).filter(SamplerPreset.is_default == True).first()
        )

    preset_dict = None
    if preset_obj:
        preset_dict = {
            "temperature": preset_obj.temperature,
            "min_p": preset_obj.min_p,
            "top_k": preset_obj.top_k,
            "top_p": preset_obj.top_p,
            "repeat_penalty": preset_obj.repeat_penalty,
            "dry_multiplier": preset_obj.dry_multiplier,
            "dry_base": preset_obj.dry_base,
            "dry_range": preset_obj.dry_range,
            "xtc_threshold": preset_obj.xtc_threshold,
            "xtc_probability": preset_obj.xtc_probability,
        }

    return ChatTurnContext(
        user=user,
        character=character,
        state=state,
        prompt=prompt,
        config=config,
        preset_dict=preset_dict,
        effective_parent_id=effective_parent_id,
        user_message_content=user_message_content,
        force_reflect=force_reflect,
    )


@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(character_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(MessageNode)
        .filter(MessageNode.character_id == character_id, MessageNode.is_active == True)
        .order_by(MessageNode.timestamp.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": m.id,
            "parent_id": m.parent_id,
            "role": m.role,
            "content": m.content,
            "variant_index": m.variant_index,
            "timestamp": m.timestamp,
        }
        for m in reversed(messages)
    ]


@router.post("/chat/clear/{character_id}")
async def clear_chat_history(character_id: int, db: Session = Depends(get_db)):
    try:
        from src.backend.db.models import JournalEntry

        # Delete all messages and journal entries for this character
        db.query(MessageNode).filter(MessageNode.character_id == character_id).delete()
        db.query(JournalEntry).filter(
            JournalEntry.character_id == character_id
        ).delete()
        # Reset current message ID and states on AgentState
        state = (
            db.query(AgentState).filter(AgentState.character_id == character_id).first()
        )
        if state:
            state.current_message_id = None
            state.location = "Living Room"
            state.clothes = "Casual"
            state.mood = "Neutral"
            state.interaction_count = 0
            state.stats = {
                "energy": 100,
                "hunger": 0,
                "happiness": 100,
                "social": 100,
                "is_sleeping": False,
                "relationship": {"score": 50, "history": [], "nickname": None},
            }
        db.commit()
        return {"status": "success", "message": "Chat history cleared successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear chat history for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    try:
        logger.info(f"[{request_id}] Chat Request: character_id={request.character_id}")
        ctx = await _prepare_chat_turn(request, db, request_id)

        result = await llama.complete(
            ctx.prompt,
            url=ctx.config.base_url,
            model=ctx.config.model_name,
            preset=ctx.preset_dict,
        )
        reply = result.get("content", "...").strip()

        # RN-003: Formatting Validation
        is_formatted = validate_narrative_formatting(reply)
        if not is_formatted:
            logger.warning(
                f"[{request_id}] AI Response failed narrative formatting validation (RN-003)."
            )
            # In a production system, we might re-prompt here.
            # For now, we log and proceed to maintain responsiveness,
            # but could append a correction instruction to the next prompt.

        parse_actions_to_state(reply, ctx.state)

        variant_count = (
            db.query(MessageNode)
            .filter(MessageNode.parent_id == ctx.effective_parent_id)
            .count()
        )
        ai_msg = MessageNode(
            character_id=ctx.character.id,
            user_id=ctx.user.id,
            role="assistant",
            content=reply,
            parent_id=ctx.effective_parent_id,
            variant_index=variant_count,
            request_id=request_id,
        )
        db.add(ai_msg)
        db.flush()
        ctx.state.current_message_id = ai_msg.id
        db.commit()

        background_tasks.add_task(
            run_consciousness_layer,
            ctx.character.id,
            ctx.user_message_content or "",
            reply,
            force_reflect=ctx.force_reflect,
        )

        latency = (
            {"total": time.perf_counter() - start} if settings.DEBUG_LATENCY else {}
        )
        logger.info(
            f"[{request_id}] Chat Success: duration={latency.get('total', 0):.3f}s"
        )
        return ChatResponse(
            reply=reply, request_id=request_id, stats=ctx.state.stats, latency=latency
        )
    except StaleDataError:
        db.rollback()
        logger.warning(
            f"[{request_id}] Chat Conflict: character state changed concurrently"
        )
        raise HTTPException(
            status_code=409,
            detail="Character state changed concurrently -- please retry.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[{request_id}] Chat Error: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Stream Request: character_id={request.character_id}")

    try:
        ctx = await _prepare_chat_turn(request, db, request_id)
    except StaleDataError:
        db.rollback()
        logger.warning(
            f"[{request_id}] Stream Conflict: character state changed concurrently"
        )
        error_msg = "Character state changed concurrently -- please retry."

        async def conflict_stream():
            yield f"data: {json.dumps({'error': error_msg, 'request_id': request_id})}\n\n"

        return StreamingResponse(
            conflict_stream(), media_type="text/event-stream", status_code=409
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[{request_id}] Stream setup error: {e}")
        logger.exception(e)
        error_msg = str(e)

        async def error_stream():
            yield f"data: {json.dumps({'error': error_msg, 'request_id': request_id})}\n\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def generate():
        full_reply = ""
        try:
            async for token in llama.complete_stream(
                ctx.prompt,
                url=ctx.config.base_url,
                model=ctx.config.model_name,
                preset=ctx.preset_dict,
            ):
                full_reply += token
                yield f"data: {json.dumps({'token': token})}\n\n"

            if full_reply.strip():
                inner_db = SessionLocal()
                try:
                    inner_state = (
                        inner_db.query(AgentState)
                        .filter(AgentState.id == ctx.state.id)
                        .first()
                    )
                    variant_count = (
                        inner_db.query(MessageNode)
                        .filter(MessageNode.parent_id == ctx.effective_parent_id)
                        .count()
                    )
                    ai_msg = MessageNode(
                        character_id=ctx.character.id,
                        user_id=ctx.user.id,
                        role="assistant",
                        content=full_reply,
                        parent_id=ctx.effective_parent_id,
                        variant_index=variant_count,
                        request_id=request_id,
                    )
                    inner_db.add(ai_msg)
                    inner_db.flush()
                    if inner_state:
                        inner_state.current_message_id = ai_msg.id
                        parse_actions_to_state(full_reply, inner_state)
                    inner_db.commit()

                    # RN-003: Formatting Validation (Stream)
                    is_formatted = validate_narrative_formatting(full_reply)
                    if not is_formatted:
                        logger.warning(
                            f"[{request_id}] AI Stream Response failed narrative formatting validation (RN-003)."
                        )

                    background_tasks.add_task(
                        run_consciousness_layer,
                        ctx.character.id,
                        ctx.user_message_content or "",
                        full_reply,
                        force_reflect=ctx.force_reflect,
                    )
                    # Return full state for reactive HUD
                    updated_state = {
                        "location": inner_state.location,
                        "clothes": inner_state.clothes,
                        "mood": inner_state.mood,
                        "interaction_count": inner_state.interaction_count,
                        "stats": inner_state.stats,
                    }
                    logger.info(
                        f"[{request_id}] Stream Success: gen_len={len(full_reply)}"
                    )
                    yield f"data: {json.dumps({'done': True, 'request_id': request_id, 'state': updated_state, 'message_id': ai_msg.id})}\n\n"
                finally:
                    inner_db.close()
            else:
                yield f"data: {json.dumps({'done': True, 'request_id': request_id})}\n\n"
        except Exception as e:
            logger.error(f"[{request_id}] Stream Error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'request_id': request_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def deactivate_subtree(node_id: int, db: Session):
    children = db.query(MessageNode).filter(MessageNode.parent_id == node_id).all()
    for child in children:
        child.is_active = False
        deactivate_subtree(child.id, db)


@router.put("/chat/message/{message_id}")
async def edit_message(
    message_id: int, req: MessageEditRequest, db: Session = Depends(get_db)
):
    logger.info(f"Backend edit_message called: id={message_id}, content={req.content}")
    msg = (
        db.query(MessageNode)
        .filter(MessageNode.id == message_id, MessageNode.is_active == True)
        .first()
    )
    if not msg:
        logger.error(
            f"Backend edit_message: message {message_id} not found or inactive"
        )
        raise HTTPException(status_code=404, detail="Message not found or inactive")

    msg.content = req.content

    # If a user message is edited, invalidate all subsequent assistant responses (and their subtrees)
    if msg.role == "user":
        logger.info(
            f"Backend edit_message: deactivating subtree for user message {message_id}"
        )
        deactivate_subtree(msg.id, db)

        # Update current_message_id to the edited message so tree can resume from here
        state = (
            db.query(AgentState)
            .filter(AgentState.character_id == msg.character_id)
            .first()
        )
        if state:
            state.current_message_id = msg.id

    db.commit()
    logger.info(f"Backend edit_message: committed successfully for {message_id}")
    return {"status": "success", "message": "Message edited successfully"}


@router.delete("/chat/message/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = (
        db.query(MessageNode)
        .filter(MessageNode.id == message_id, MessageNode.is_active == True)
        .first()
    )
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found or inactive")

    msg.is_active = False
    deactivate_subtree(msg.id, db)

    # Update current_message_id to parent if this was the current message
    state = (
        db.query(AgentState).filter(AgentState.character_id == msg.character_id).first()
    )
    if state and state.current_message_id == msg.id:
        state.current_message_id = msg.parent_id

    db.commit()
    return {"status": "success", "message": "Message deleted successfully"}
