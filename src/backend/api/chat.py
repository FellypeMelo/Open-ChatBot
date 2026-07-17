import json
import logging
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Dict, Any, Optional

from src.backend.core.deps import llama_client as llama, vector_store, brain
from src.backend.core.orchestration.validator import validate_narrative_formatting
from src.backend.core.context.macros import render_macros
from src.backend.core.engine.engine import update_needs, evolve_character
from src.backend.core.engine.state_transitions import (
    ACTIONS_CONFIG,
    apply_action_stats,
    parse_actions_to_state,
)
from src.backend.db.database import get_db, SessionLocal
from src.backend.db.models import (
    AgentState,
    Character,
    User,
    MessageNode,
    Chat,
    JournalEntry,
    SamplerPreset,
)
import uuid
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _active_branch_messages(
    db: Session,
    character_id: int,
    chat_id: Optional[int],
    leaf_id: Optional[int],
    limit: int,
) -> List[MessageNode]:
    """The last `limit` messages on the ACTIVE branch -- the parent chain from
    the selected leaf. Walking the chain (rather than a flat is_active+timestamp
    fetch) excludes non-selected regenerate variants, so reflection never
    summarizes a reroll the user swiped away (PZ-02b). Falls back to the flat
    fetch when no leaf id is available."""
    if leaf_id is None:
        q = db.query(MessageNode).filter(
            MessageNode.character_id == character_id,
            MessageNode.is_active == True,  # noqa: E712
        )
        if chat_id is not None:
            q = q.filter(MessageNode.chat_id == chat_id)
        rows = q.order_by(MessageNode.timestamp.desc()).limit(limit).all()
        return list(reversed(rows))

    chain: List[MessageNode] = []
    curr = leaf_id
    while curr is not None and len(chain) < limit:
        node = db.query(MessageNode).filter(MessageNode.id == curr).first()
        if node is None or not node.is_active:
            break
        chain.append(node)
        curr = node.parent_id
    chain.reverse()
    return chain


async def run_consciousness_layer(
    character_id: int,
    user_message: str,
    ai_response: str,
    force_reflect: bool = False,
    chat_id: Optional[int] = None,
    store_memory: bool = True,
    message_id: Optional[int] = None,
    reflected_at_count: Optional[int] = None,
):
    """Background task for memory and evolution."""
    try:
        db = SessionLocal()
        try:
            # 1. Store memory, scoped to (character, chat) so this turn can only
            # ever be recalled inside its own chat/session. Skipped for synthetic
            # (quick-action) turns whose canned first-person text would otherwise
            # accumulate and self-retrieve on every repeat (PZ-04). Tagged with the
            # assistant message id so it can be purged when that node is edited or
            # deleted (PZ-01).
            if store_memory:
                # Keep only the selected/latest variant's memory for a turn: a
                # regenerate creates a new sibling under the same parent, so purge
                # the superseded siblings' memories before storing this one, so
                # only the chosen reply stays retrievable (PZ-01b).
                if message_id is not None:
                    node = (
                        db.query(MessageNode)
                        .filter(MessageNode.id == message_id)
                        .first()
                    )
                    if node is not None and node.parent_id is not None:
                        siblings = (
                            db.query(MessageNode.id)
                            .filter(
                                MessageNode.parent_id == node.parent_id,
                                MessageNode.id != message_id,
                            )
                            .all()
                        )
                        if siblings:
                            await vector_store.delete_by_message_ids(
                                [s.id for s in siblings]
                            )
                memory_meta = {"character_id": character_id}
                if chat_id is not None:
                    memory_meta["chat_id"] = chat_id
                if message_id is not None:
                    memory_meta["message_id"] = message_id
                await vector_store.add_memory(
                    f"User: {user_message}\nAI: {ai_response}",
                    metadata=memory_meta,
                )

            # 2. Reflect & Evolve (only on interval or force). Reflect over the
            # ACTIVE branch from the selected leaf so discarded edit/delete
            # branches (PZ-02) and non-selected regenerate variants (PZ-02b) can
            # never leak into the character's permanent state.
            if force_reflect:
                messages = _active_branch_messages(
                    db, character_id, chat_id, message_id, settings.REFLECTION_INTERVAL
                )
                msg_dicts = [
                    {"role": m.role, "content": m.content} for m in messages
                ]

                reflection = await brain.reflect(
                    msg_dicts, window_size=settings.REFLECTION_INTERVAL
                )
                # Mark this reflection window as consumed only now that it
                # succeeded, so a failed boundary turn is retried next time rather
                # than skipped forever (RF-04). The AgentState mirror is written
                # atomically inside evolve_character, guarded so a chat switch
                # during reflect() can't stamp it onto a different chat.
                evolve_character(
                    db,
                    character_id,
                    reflection,
                    reflected_at_count=reflected_at_count,
                    active_chat_id=chat_id,
                )

                # The Chat row is the per-chat source of truth for the reflecting
                # chat: stamp it explicitly (by chat_id), correct regardless of any
                # concurrent switch to another chat.
                if reflected_at_count is not None and chat_id is not None:
                    db.query(Chat).filter(Chat.id == chat_id).update(
                        {Chat.last_reflected_at_count: reflected_at_count},
                        synchronize_session=False,
                    )
                    db.commit()

                logger.info(
                    f"Consciousness Layer: Reflection complete for character {character_id}"
                )
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Consciousness layer error: {e}")


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
    chat_id: Optional[int] = None
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
        chat_id: Optional[int] = None,
        is_action: bool = False,
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
        self.chat_id = chat_id
        self.is_action = is_action


def _sync_state_to_chat(db: Session, state: AgentState, chat_id: Optional[int]):
    """Persist AgentState's conversation-local fields (pointer/summary/counter)
    into its Chat row so switching away and back restores this session."""
    if not chat_id:
        return
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        chat.current_message_id = state.current_message_id
        chat.active_summary = state.active_summary or ""
        chat.interaction_count = state.interaction_count or 0
        chat.last_reflected_at_count = state.last_reflected_at_count or 0
        chat.updated_at = datetime.now(timezone.utc)


def _load_chat_into_state(state: AgentState, chat: Chat):
    """Mirror a Chat's conversation-local snapshot onto the live AgentState."""
    state.current_message_id = chat.current_message_id
    state.active_summary = chat.active_summary or ""
    state.interaction_count = chat.interaction_count or 0
    state.last_reflected_at_count = chat.last_reflected_at_count or 0
    state.active_chat_id = chat.id


def _persist_assistant_reply(
    db: Session,
    state: Optional[AgentState],
    ctx: "ChatTurnContext",
    reply: str,
    request_id: str,
) -> MessageNode:
    """Persist an assistant reply as the next variant under the turn's parent,
    advance the conversation pointer, and commit. Shared by /chat and /chat/stream
    so the two paths can never diverge. `state` may be None (a stream re-query
    that failed): the message is still saved, only the pointer update is skipped.
    Callers apply parse_actions_to_state before calling."""
    variant_count = (
        db.query(MessageNode)
        .filter(MessageNode.parent_id == ctx.effective_parent_id)
        .count()
    )
    ai_msg = MessageNode(
        character_id=ctx.character.id,
        chat_id=ctx.chat_id,
        user_id=ctx.user.id,
        role="assistant",
        content=reply,
        parent_id=ctx.effective_parent_id,
        variant_index=variant_count,
        request_id=request_id,
    )
    db.add(ai_msg)
    db.flush()
    if state is not None:
        state.current_message_id = ai_msg.id
        _sync_state_to_chat(db, state, ctx.chat_id)
    db.commit()
    return ai_msg


def _resolve_active_chat(
    db: Session,
    character: Character,
    state: AgentState,
    requested_chat_id: Optional[int],
    user: Optional[User],
) -> Chat:
    """Resolve which Chat/session this turn belongs to, switching if the client
    asked for a different chat than the currently-active one. Lazily creates a
    first chat for a character that has none (adopting its existing live
    conversation), so a config-less clone always resolves a valid session."""
    target = None
    if requested_chat_id is not None:
        target = (
            db.query(Chat)
            .filter(Chat.id == requested_chat_id, Chat.character_id == character.id)
            .first()
        )
        if not target:
            raise HTTPException(
                status_code=400, detail="chat_id does not belong to this character"
            )
    elif state.active_chat_id:
        target = db.query(Chat).filter(Chat.id == state.active_chat_id).first()

    if target is None:
        # No chat yet: adopt the character's existing live conversation into a
        # first Chat row so pre-Chat-entity history stays intact.
        target = Chat(
            character_id=character.id,
            user_id=(user.id if user else None),
            title="New Chat",
            current_message_id=state.current_message_id,
            active_summary=state.active_summary or "",
            interaction_count=state.interaction_count or 0,
        )
        db.add(target)
        db.flush()
        state.active_chat_id = target.id
        # Adopt any pre-existing (pre-Chat-entity) messages/journals for this
        # character into this first chat, so a later "New Chat" doesn't inherit
        # or display them.

        db.query(MessageNode).filter(
            MessageNode.character_id == character.id,
            MessageNode.chat_id.is_(None),
        ).update({MessageNode.chat_id: target.id}, synchronize_session=False)
        db.query(JournalEntry).filter(
            JournalEntry.character_id == character.id,
            JournalEntry.chat_id.is_(None),
        ).update({JournalEntry.chat_id: target.id}, synchronize_session=False)
        db.flush()
        return target

    # Switching to a different chat: save the outgoing session, load the target.
    if state.active_chat_id != target.id:
        _sync_state_to_chat(db, state, state.active_chat_id)
        _load_chat_into_state(state, target)

    return target


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

    # Resolve the chat/session this turn belongs to BEFORE bumping the counter,
    # so switching to another chat restores that chat's interaction_count first.
    chat = _resolve_active_chat(db, character, state, request.chat_id, user)

    state.stats = update_needs(state.stats, datetime.now(timezone.utc))
    state.interaction_count += 1
    # Trigger when at least REFLECTION_INTERVAL turns have passed since the last
    # SUCCESSFUL reflection (not a bare modulo): a reflection due on a boundary
    # turn that fails is caught on the next turn instead of skipped forever (RF-04).
    force_reflect = (
        state.interaction_count - (state.last_reflected_at_count or 0)
        >= settings.REFLECTION_INTERVAL
    )
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
        force_reflect = (
            state.interaction_count - (state.last_reflected_at_count or 0)
            >= settings.REFLECTION_INTERVAL
        )

    effective_parent_id = (
        request.parent_id if request.parent_id is not None else state.current_message_id
    )
    # Reject a client-supplied parent_id that belongs to a different character
    # or a different chat (cross-thread grafting) -- otherwise the history walk
    # would splice another conversation's messages into this prompt. Fall back
    # to this chat's own current pointer.
    if effective_parent_id is not None:
        parent_node = (
            db.query(MessageNode)
            .filter(MessageNode.id == effective_parent_id)
            .first()
        )
        if parent_node is not None and (
            parent_node.character_id != character.id
            or (parent_node.chat_id is not None and parent_node.chat_id != chat.id)
        ):
            logger.warning(
                f"[{request_id}] Rejected cross-thread parent_id={effective_parent_id} "
                f"(char {parent_node.character_id}/chat {parent_node.chat_id}) for "
                f"char {character.id}/chat {chat.id}; falling back to chat pointer."
            )
            effective_parent_id = (
                state.current_message_id
                if state.current_message_id != effective_parent_id
                else None
            )
    user_message_content = request.message

    is_action = bool(request.action_id and request.action_id in ACTIONS_CONFIG)
    if is_action:
        action_cfg = ACTIONS_CONFIG[request.action_id]
        user_message_content = action_cfg["message"]
        request.message = user_message_content
        state.stats = apply_action_stats(state.stats, action_cfg.get("stats", {}))

    if not user_message_content and effective_parent_id:
        last_msg = (
            db.query(MessageNode).filter(MessageNode.id == effective_parent_id).first()
        )
        if last_msg and last_msg.role == "user":
            user_message_content = last_msg.content

    if request.message:
        user_msg = MessageNode(
            character_id=character.id,
            chat_id=chat.id,
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
            .filter(
                MessageNode.id == curr_id,
                MessageNode.is_active == True,
                # Stay within this chat: match its chat_id, or NULL for legacy
                # nodes adopted into a lazily-created first chat.
                or_(
                    MessageNode.chat_id == chat.id,
                    MessageNode.chat_id.is_(None),
                ),
            )
            .first()
        )
        if not m:
            break
        history.append({"role": m.role, "content": m.content})
        curr_id = m.parent_id
    history.reverse()

    # Drop the trailing history line when it is the same user turn we re-append
    # below as "{user}: {message}". This is the last line in BOTH paths: a normal
    # send (the just-inserted user node) and a regenerate (message is None, so
    # effective_parent_id still points at that user node). Without this, a
    # regenerate feeds the model the user's last line twice in a row.
    prompt_history = history
    if history and user_message_content:
        last = history[-1]
        if last.get("role") == "user" and last.get("content") == user_message_content:
            prompt_history = history[:-1]

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
        history=prompt_history,
        db=db,
        chat_id=chat.id,
    )

    config = request.config or LLMConfig()


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
        chat_id=chat.id,
        is_action=is_action,
    )


@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(
    character_id: int,
    chat_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Messages for a character, scoped to one chat/session. Defaults to the
    character's active chat so the current UI (which passes only character_id)
    never mixes messages from different sessions."""
    q = db.query(MessageNode).filter(
        MessageNode.character_id == character_id, MessageNode.is_active == True
    )
    if chat_id is None:
        state = (
            db.query(AgentState)
            .filter(AgentState.character_id == character_id)
            .first()
        )
        chat_id = state.active_chat_id if state else None
    if chat_id is not None:
        q = q.filter(
            or_(MessageNode.chat_id == chat_id, MessageNode.chat_id.is_(None))
        )
    messages = q.order_by(MessageNode.timestamp.desc()).limit(100).all()
    return [
        {
            "id": m.id,
            "parent_id": m.parent_id,
            "role": m.role,
            "content": m.content,
            "variant_index": m.variant_index,
            "timestamp": m.timestamp,
            "chat_id": m.chat_id,
        }
        for m in reversed(messages)
    ]


class ChatUpdateRequest(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class NewChatRequest(BaseModel):
    # The opening greeting to seed. Either explicit text, or an index into the
    # character's greetings ([first_mes, *alternate_greetings]). If neither is
    # given, greeting #1 (first_mes) is used when present.
    greeting: Optional[str] = None
    greeting_index: Optional[int] = None


def _character_greetings(character: Character) -> List[str]:
    """The ordered greeting list: first_mes is #1, alternate_greetings follow."""
    greetings = []
    if getattr(character, "first_mes", None):
        greetings.append(character.first_mes)
    alts = getattr(character, "alternate_greetings", None) or []
    greetings.extend([g for g in alts if g])
    return greetings


@router.post("/chat/new/{character_id}")
async def new_chat(
    character_id: int,
    req: Optional[NewChatRequest] = Body(default=None),
    db: Session = Depends(get_db),
):
    """Start a fresh chat/session with a character WITHOUT destroying the
    previous one. Saves the currently-active chat's live state, creates a new
    Chat row, points the character at it with reset conversation-local fields
    (persona/relationship/stats persist across a character's chats), and seeds
    the chosen opening greeting as the first assistant message."""
    user = User.get_or_create_active(db)
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    state = character.state or AgentState(character_id=character.id)
    if not state.id:
        db.add(state)
        db.flush()

    # Persist the outgoing session so it can be revisited later.
    _sync_state_to_chat(db, state, state.active_chat_id)

    fresh = Chat(
        character_id=character.id,
        user_id=user.id,
        title="New Chat",
        current_message_id=None,
        active_summary="",
        interaction_count=0,
        last_reflected_at_count=0,
    )
    db.add(fresh)
    db.flush()

    state.active_chat_id = fresh.id
    state.current_message_id = None
    state.active_summary = ""
    state.interaction_count = 0
    # Reset the reflection checkpoint too, or force_reflect goes negative and
    # suppresses reflection for dozens of turns after a reset (RF-04).
    state.last_reflected_at_count = 0

    # Resolve the opening greeting to seed (explicit text > index > first_mes).
    greetings = _character_greetings(character)
    greeting_text = None
    if req and req.greeting is not None:
        greeting_text = req.greeting
    elif req and req.greeting_index is not None:
        if 0 <= req.greeting_index < len(greetings):
            greeting_text = greetings[req.greeting_index]
    elif greetings:
        greeting_text = greetings[0]

    if greeting_text and greeting_text.strip():
        rendered = render_macros(greeting_text, character.name, user.name)
        greeting_msg = MessageNode(
            character_id=character.id,
            chat_id=fresh.id,
            user_id=user.id,
            role="assistant",
            content=rendered,
            parent_id=None,
            request_id=None,
        )
        db.add(greeting_msg)
        db.flush()
        state.current_message_id = greeting_msg.id
        fresh.current_message_id = greeting_msg.id

    db.commit()
    return {"chat_id": fresh.id, "title": fresh.title}


@router.get("/chats/{character_id}", response_model=List[Dict[str, Any]])
async def list_chats(character_id: int, db: Session = Depends(get_db)):
    """List a character's chats (newest first) for a chat-picker sidebar."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    active_id = character.state.active_chat_id if character.state else None
    chats = (
        db.query(Chat)
        .filter(Chat.character_id == character_id)
        .order_by(Chat.updated_at.desc())
        .all()
    )
    # Single grouped COUNT instead of one query per chat (avoids an N+1).
    counts = dict(
        db.query(MessageNode.chat_id, func.count(MessageNode.id))
        .filter(MessageNode.chat_id.in_([c.id for c in chats]))
        .group_by(MessageNode.chat_id)
        .all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "is_archived": bool(c.is_archived),
            "is_active": c.id == active_id,
            "message_count": counts.get(c.id, 0),
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in chats
    ]


@router.put("/chat/{chat_id}")
async def update_chat(
    chat_id: int, req: ChatUpdateRequest, db: Session = Depends(get_db)
):
    """Rename or archive a chat."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if req.title is not None:
        chat.title = req.title
    if req.is_archived is not None:
        chat.is_archived = req.is_archived
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "id": chat.id,
        "title": chat.title,
        "is_archived": bool(chat.is_archived),
    }


@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """Delete a single chat: its messages, journals and vector memories only.
    Sibling chats of the same character are untouched. If it was the active
    chat, repoint the character to its most recent remaining chat."""

    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    character_id = chat.character_id
    state = (
        db.query(AgentState).filter(AgentState.character_id == character_id).first()
    )
    was_active = bool(state and state.active_chat_id == chat_id)

    # Null pointers that reference rows we are about to delete (FK-safe order).
    if was_active:
        state.current_message_id = None
    if state and state.active_chat_id == chat_id:
        state.active_chat_id = None
    chat.current_message_id = None
    db.flush()

    db.query(MessageNode).filter(MessageNode.chat_id == chat_id).delete(
        synchronize_session=False
    )
    db.query(JournalEntry).filter(JournalEntry.chat_id == chat_id).delete(
        synchronize_session=False
    )
    db.delete(chat)
    db.flush()

    if was_active:
        remaining = (
            db.query(Chat)
            .filter(Chat.character_id == character_id)
            .order_by(Chat.updated_at.desc())
            .first()
        )
        if remaining:
            _load_chat_into_state(state, remaining)
        else:
            state.current_message_id = None
            state.active_summary = ""
            state.interaction_count = 0
            state.last_reflected_at_count = 0
    db.commit()

    removed = await vector_store.clear_chat_memories(chat_id)
    return {"status": "success", "removed_memories": removed}


@router.post("/chat/clear/{character_id}")
async def clear_chat_history(character_id: int, db: Session = Depends(get_db)):
    """Destructive full reset for a character: wipes ALL of its chats, messages,
    journals, summary and RAG memories and resets its live state. This is the
    'nuke everything' path -- use POST /chat/new for a non-destructive fresh
    session that keeps prior chats."""
    try:

        # Reset AgentState first and null its pointers into rows we will delete
        # (FK-safe once PRAGMA foreign_keys=ON is in effect).
        state = (
            db.query(AgentState).filter(AgentState.character_id == character_id).first()
        )
        if state:
            state.current_message_id = None
            state.active_chat_id = None
            state.location = "Living Room"
            state.clothes = "Casual"
            state.mood = "Neutral"
            state.interaction_count = 0
            state.last_reflected_at_count = 0
            # Wipe the running summary too; otherwise summary-based context
            # (including hallucinated content) survives a reset.
            state.active_summary = ""
            state.stats = {
                "energy": 100,
                "hunger": 0,
                "happiness": 100,
                "social": 100,
                "is_sleeping": False,
                # Without last_update, update_needs early-returns forever and
                # time-decay of needs freezes for the rest of the character's life.
                "last_update": datetime.now(timezone.utc).isoformat(),
                "relationship": {"score": 50, "history": [], "nickname": None},
            }
        # Null chat->message pointers before deleting the messages they reference.
        db.query(Chat).filter(Chat.character_id == character_id).update(
            {Chat.current_message_id: None}, synchronize_session=False
        )
        db.flush()

        # Delete all messages, journals and chats for this character.
        db.query(MessageNode).filter(MessageNode.character_id == character_id).delete(
            synchronize_session=False
        )
        db.query(JournalEntry).filter(
            JournalEntry.character_id == character_id
        ).delete(synchronize_session=False)
        db.query(Chat).filter(Chat.character_id == character_id).delete(
            synchronize_session=False
        )
        db.commit()

        # Purge this character's RAG memories. Without this, a reset leaves the
        # vector store intact and old/hallucinated memories get re-injected into
        # future prompts (context poisoning).
        await vector_store.clear_character_memories(character_id)

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

        # Only persist + remember a real reply. An empty/failed generation must
        # not leave a blank assistant node or a "User: ..\nAI: " memory (PZ-07;
        # mirrors the /chat/stream guard).
        if reply.strip():
            parse_actions_to_state(reply, ctx.state)
            ai_msg = _persist_assistant_reply(db, ctx.state, ctx, reply, request_id)

            background_tasks.add_task(
                run_consciousness_layer,
                ctx.character.id,
                ctx.user_message_content or "",
                reply,
                force_reflect=ctx.force_reflect,
                chat_id=ctx.chat_id,
                store_memory=not ctx.is_action,
                message_id=ai_msg.id,
                reflected_at_count=ctx.state.interaction_count,
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
                    if inner_state:
                        parse_actions_to_state(full_reply, inner_state)
                    ai_msg = _persist_assistant_reply(
                        inner_db, inner_state, ctx, full_reply, request_id
                    )

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
                        chat_id=ctx.chat_id,
                        store_memory=not ctx.is_action,
                        message_id=ai_msg.id,
                        reflected_at_count=ctx.state.interaction_count,
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


def deactivate_subtree(node_id: int, db: Session) -> List[int]:
    """Mark every descendant of node_id inactive (the node itself is untouched)
    and return the ids of the nodes deactivated, so callers can purge those
    turns' vector memories (PZ-01). Iterative, level-batched walk -- avoids
    per-node queries and unbounded recursion on a long linear message chain."""
    deactivated: List[int] = []
    frontier = [node_id]
    while frontier:
        children = (
            db.query(MessageNode)
            .filter(MessageNode.parent_id.in_(frontier))
            .all()
        )
        if not children:
            break
        for child in children:
            child.is_active = False
        frontier = [child.id for child in children]
        deactivated.extend(frontier)
    return deactivated


def _set_branch_pointer(
    db: Session,
    state: Optional[AgentState],
    target_chat_id: Optional[int],
    new_pointer: Optional[int],
):
    """Repoint the resume pointer of the chat that OWNS the edited/deleted node.

    If that chat is the live/active one (or the node is a legacy NULL-chat node
    adopted into it), update the AgentState mirror. Otherwise update the owning
    Chat row directly -- writing the live AgentState for a node in a background
    chat would silently move the foreground chat's resume pointer to another
    chat's message (TF-02)."""
    if state is not None and (
        target_chat_id is None or state.active_chat_id == target_chat_id
    ):
        state.current_message_id = new_pointer
    elif target_chat_id is not None:
        db.query(Chat).filter(Chat.id == target_chat_id).update(
            {Chat.current_message_id: new_pointer}, synchronize_session=False
        )


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

    # Collect the message ids whose stale vector memories must be purged (PZ-01).
    purge_ids: List[int] = []
    if msg.role == "user":
        # Editing a user turn invalidates every reply below it (and their
        # subtrees): purge those turns' memories.
        logger.info(
            f"Backend edit_message: deactivating subtree for user message {message_id}"
        )
        purge_ids = deactivate_subtree(msg.id, db)

        # Resume the OWNING chat from the edited message. Target that chat
        # specifically so an edit in a background chat never repoints the
        # active chat's live pointer (TF-02).
        state = (
            db.query(AgentState)
            .filter(AgentState.character_id == msg.character_id)
            .first()
        )
        _set_branch_pointer(db, state, msg.chat_id, msg.id)
    elif msg.role == "assistant":
        # The edited reply's stored memory holds the OLD AI text; drop it so the
        # pre-edit content can't resurface via RAG (its metadata is keyed on this
        # exact assistant node id).
        purge_ids = [msg.id]

    db.commit()
    if purge_ids:
        await vector_store.delete_by_message_ids(purge_ids)
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
    deactivated = [msg.id] + deactivate_subtree(msg.id, db)

    # If the deleted node was the resume pointer of its OWNING chat, move that
    # pointer to the parent. Target the right chat: a delete in a background chat
    # must repoint THAT chat (not the live AgentState, which mirrors the active
    # chat) so neither is left dangling at a deactivated node (TF-02).
    state = (
        db.query(AgentState).filter(AgentState.character_id == msg.character_id).first()
    )
    if state is not None and (
        msg.chat_id is None or state.active_chat_id == msg.chat_id
    ):
        if state.current_message_id == msg.id:
            state.current_message_id = msg.parent_id
    elif msg.chat_id is not None:
        owning = db.query(Chat).filter(Chat.id == msg.chat_id).first()
        if owning and owning.current_message_id == msg.id:
            owning.current_message_id = msg.parent_id

    db.commit()
    # Purge the deleted turn's (and its subtree's) vector memories (PZ-01).
    await vector_store.delete_by_message_ids(deactivated)
    return {"status": "success", "message": "Message deleted successfully"}
