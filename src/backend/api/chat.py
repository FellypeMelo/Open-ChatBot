import json
import logging
import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from src.backend.core.engine.llm import LlamaClient
from src.backend.core.orchestration.bridge import Brain
from src.backend.core.orchestration.validator import validate_narrative_formatting
from src.backend.core.memory.vector_store import VectorStore
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
    loc_match = re.search(r'\*\*(?:enters|walks into|arrives at|is now in) (.+?)\*\*', ai_response, re.IGNORECASE)
    if loc_match:
        new_loc = loc_match.group(1).strip().strip('.')
        # Strip articles
        new_loc = re.sub(r'^(?:The|A|An)\s+', '', new_loc, flags=re.IGNORECASE)
        new_loc = new_loc.capitalize()
        if new_loc != state.location:
            logger.info(f"State Update: Location -> {new_loc}")
            state.location = new_loc

    # Pattern for outfit: **changes into [outfit]** or **is wearing [outfit]**
    outfit_match = re.search(r'\*\*(?:changes into|puts on|is wearing|dresses in) (.+?)\*\*', ai_response, re.IGNORECASE)
    if outfit_match:
        new_outfit = outfit_match.group(1).strip().strip('.')
        # Strip articles
        new_outfit = re.sub(r'^(?:The|A|An)\s+', '', new_outfit, flags=re.IGNORECASE)
        new_outfit = new_outfit.capitalize()
        if new_outfit != state.clothes:
            logger.info(f"State Update: Clothes -> {new_outfit}")
            state.clothes = new_outfit

    # Physiological stats updates based on keywords in actions
    stats = dict(state.stats) if state.stats else {}
    
    # Check for eating/drinking
    eat_match = re.search(r'\*\*(?:eats|takes a bite of|chews on|drinks|sips|consumes|devours) (.+?)\*\*', ai_response, re.IGNORECASE)
    if eat_match:
        old_hunger = stats.get("hunger", 0)
        new_hunger = max(0, old_hunger - 30)
        stats["hunger"] = new_hunger
        logger.info(f"State Update: Hunger {old_hunger}% -> {new_hunger}% due to eating action")

    # Check for sleeping
    sleep_match = re.search(r'\*\*(?:goes to sleep|falls asleep|nods off|sleeps|rests her eyes)\*\*', ai_response, re.IGNORECASE)
    if sleep_match:
        stats["is_sleeping"] = True
        logger.info("State Update: is_sleeping -> True due to sleeping action")
        
    # Check for waking up
    wake_match = re.search(r'\*\*(?:wakes up|stretches and yawns|wakes)\*\*', ai_response, re.IGNORECASE)
    if wake_match:
        stats["is_sleeping"] = False
        logger.info("State Update: is_sleeping -> False due to waking action")

    state.stats = stats
router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)

async def run_consciousness_layer(character_id: int, user_message: str, ai_response: str, force_reflect: bool = False):
    """Background task for memory and evolution."""
    try:
        db = SessionLocal()
        try:
            # 1. Store memory (always)
            await vector_store.add_memory(f"User: {user_message}\nAI: {ai_response}", metadata={"character_id": character_id})
            
            # 2. Reflect & Evolve (only on interval or force)
            if force_reflect:
                # Fetch last 20 messages for deep context
                messages = db.query(MessageNode).filter(MessageNode.character_id == character_id).order_by(MessageNode.timestamp.desc()).limit(20).all()
                msg_dicts = [{"role": m.role, "content": m.content} for m in reversed(messages)]
                
                reflection = await brain.reflect(msg_dicts, window_size=20)
                evolve_character(db, character_id, reflection)
                logger.info(f"Consciousness Layer: Reflection complete for character {character_id}")
        finally:
            db.close()
            import gc
            gc.collect()
    except Exception as e:
        logger.exception(f"Consciousness layer error: {e}")

ACTIONS_CONFIG = {
    "hug": {
        "message": "*I step forward and wrap my arms around you in a warm, gentle hug.*",
        "stats": {
            "happiness": 5,
            "social": 10,
            "relationship_score": 2
        }
    },
    "pat_head": {
        "message": "*I reach out and pat your head gently, smiling softly.*",
        "stats": {
            "happiness": 3,
            "social": 5,
            "relationship_score": 1
        }
    },
    "tease": {
        "message": "*I look at you with a playful smirk, teasing you lightly.*",
        "stats": {
            "happiness": 2,
            "social": 8,
            "relationship_score": 1
        }
    },
    "hold_hand": {
        "message": "*I slide my hand into yours, holding it gently.*",
        "stats": {
            "happiness": 4,
            "social": 8,
            "relationship_score": 2
        }
    },
    "coffee": {
        "message": "*I hand you a hot, freshly brewed cup of black coffee.*",
        "stats": {
            "hunger": -10,
            "energy": 15,
            "relationship_score": 2
        }
    },
    "croissant": {
        "message": "*I offer you a warm, freshly baked chocolate croissant.*",
        "stats": {
            "hunger": -35,
            "energy": 5,
            "relationship_score": 3
        }
    },
    "book": {
        "message": "*I present you with a beautifully bound, vintage book.*",
        "stats": {
            "happiness": 8,
            "social": 5,
            "relationship_score": 4
        }
    },
    "necklace": {
        "message": "*I hand you a small velvet box containing a delicate silver necklace.*",
        "stats": {
            "happiness": 15,
            "social": 10,
            "relationship_score": 8
        }
    }
}

class LLMConfig(BaseModel):
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    preset_id: Optional[int] = None

class ChatRequest(BaseModel):
    message: Optional[str] = None
    character_id: int = 1
    parent_id: Optional[int] = None
    config: Optional[LLMConfig] = None
    action_id: Optional[str] = None

class MessageEditRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    reply: str
    request_id: str
    stats: Dict[str, Any] = {}
    latency: Dict[str, float] = {}

@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(character_id: int, db: Session = Depends(get_db)):
    messages = db.query(MessageNode).filter(
        MessageNode.character_id == character_id,
        MessageNode.is_active == True
    ).order_by(MessageNode.timestamp.desc()).limit(100).all()
    return [{
        "id": m.id,
        "parent_id": m.parent_id,
        "role": m.role,
        "content": m.content,
        "variant_index": m.variant_index,
        "timestamp": m.timestamp
    } for m in reversed(messages)]

@router.post("/chat/clear/{character_id}")
async def clear_chat_history(character_id: int, db: Session = Depends(get_db)):
    try:
        from src.backend.db.models import JournalEntry
        # Delete all messages and journal entries for this character
        db.query(MessageNode).filter(MessageNode.character_id == character_id).delete()
        db.query(JournalEntry).filter(JournalEntry.character_id == character_id).delete()
        # Reset current message ID and states on AgentState
        state = db.query(AgentState).filter(AgentState.character_id == character_id).first()
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
                "relationship": {
                    "score": 50,
                    "history": [],
                    "nickname": None
                }
            }
        db.commit()
        return {"status": "success", "message": "Chat history cleared successfully."}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear chat history for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    try:
        logger.info(f"[{request_id}] Chat Request: character_id={request.character_id}")
        user = db.query(User).filter(User.is_active == True).first() or User(name="User", gender="Unknown")
        if not user.id: db.add(user); db.flush()

        character = db.query(Character).filter(Character.id == request.character_id).first() or Character.get_default(db)
        state = character.state or AgentState(character_id=character.id)
        if not state.id: db.add(state); db.flush()

        state.stats = update_needs(state.stats, datetime.now(timezone.utc))
        state.interaction_count += 1
        force_reflect = (state.interaction_count % 20 == 0)
        
        effective_parent_id = request.parent_id if request.parent_id is not None else state.current_message_id
        user_message_content = request.message

        if request.action_id and request.action_id in ACTIONS_CONFIG:
            action_cfg = ACTIONS_CONFIG[request.action_id]
            user_message_content = action_cfg["message"]
            request.message = user_message_content
            
            stat_mod = action_cfg.get("stats", {})
            stats = dict(state.stats) if state.stats else {}
            stats["energy"] = max(0, min(100, stats.get("energy", 100) + stat_mod.get("energy", 0)))
            stats["hunger"] = max(0, min(100, stats.get("hunger", 0) + stat_mod.get("hunger", 0)))
            stats["happiness"] = max(0, min(100, stats.get("happiness", 100) + stat_mod.get("happiness", 0)))
            stats["social"] = max(0, min(100, stats.get("social", 100) + stat_mod.get("social", 0)))
            
            relationship = stats.get("relationship", {})
            if not isinstance(relationship, dict):
                relationship = {"score": 50}
            old_score = relationship.get("score", 50)
            relationship["score"] = max(0, min(100, old_score + stat_mod.get("relationship_score", 0)))
            stats["relationship"] = relationship
            
            state.stats = stats

        if not user_message_content and effective_parent_id:
            last_msg = db.query(MessageNode).filter(MessageNode.id == effective_parent_id).first()
            if last_msg and last_msg.role == "user":
                user_message_content = last_msg.content

        if request.message:
            user_msg = MessageNode(
                character_id=character.id, 
                user_id=user.id, 
                role="user", 
                content=request.message,
                parent_id=effective_parent_id,
                request_id=request_id
            )
            db.add(user_msg)
            db.flush()
            effective_parent_id = user_msg.id
            state.current_message_id = user_msg.id

        history = []
        curr_id = effective_parent_id
        while curr_id and len(history) < 50:
            m = db.query(MessageNode).filter(MessageNode.id == curr_id, MessageNode.is_active == True).first()
            if not m: break
            history.append({"role": m.role, "content": m.content})
            curr_id = m.parent_id
        history.reverse()

        prompt = await brain.build_prompt(user_message_content or "", character, {"location": state.location, "mood": state.mood, "stats": state.stats, "active_summary": getattr(state, "active_summary", "")}, user=user, history=history[:-1] if request.message else history, db=db)
        
        # Extract config for dynamic LLM routing
        config = request.config or LLMConfig()
        
        from src.backend.db.models import SamplerPreset
        if config.preset_id:
            preset_obj = db.query(SamplerPreset).filter(SamplerPreset.id == config.preset_id).first()
        else:
            preset_obj = db.query(SamplerPreset).filter(SamplerPreset.is_default == True).first()
            
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

        result = await llama.complete(
            prompt, 
            url=config.base_url, 
            model=config.model_name,
            preset=preset_dict
        )
        reply = result.get("content", "...").strip()

        # RN-003: Formatting Validation
        is_formatted = validate_narrative_formatting(reply)
        if not is_formatted:
            logger.warning(f"[{request_id}] AI Response failed narrative formatting validation (RN-003).")
            # In a production system, we might re-prompt here. 
            # For now, we log and proceed to maintain responsiveness, 
            # but could append a correction instruction to the next prompt.

        parse_actions_to_state(reply, state)

        variant_count = db.query(MessageNode).filter(MessageNode.parent_id == effective_parent_id).count()
        ai_msg = MessageNode(
            character_id=character.id, 
            user_id=user.id, 
            role="assistant", 
            content=reply,
            parent_id=effective_parent_id,
            variant_index=variant_count,
            request_id=request_id
        )
        db.add(ai_msg)
        db.flush()
        state.current_message_id = ai_msg.id
        db.commit()
        
        background_tasks.add_task(run_consciousness_layer, character.id, user_message_content or "", reply, force_reflect=force_reflect)

        latency = {"total": time.perf_counter() - start} if settings.DEBUG_LATENCY else {}
        logger.info(f"[{request_id}] Chat Success: duration={latency.get('total', 0):.3f}s")
        return ChatResponse(reply=reply, request_id=request_id, stats=state.stats, latency=latency)
    except Exception as e:
        db.rollback()
        logger.error(f"[{request_id}] Chat Error: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Stream Request: character_id={request.character_id}")
    user = db.query(User).filter(User.is_active == True).first() or User(name="User", gender="Unknown")
    if not user.id: db.add(user); db.flush()

    character = db.query(Character).filter(Character.id == request.character_id).first() or Character.get_default(db)
    state = character.state or AgentState(character_id=character.id)
    if not state.id: db.add(state); db.flush()

    state.stats = update_needs(state.stats, datetime.now(timezone.utc))
    state.interaction_count += 1
    force_reflect = (state.interaction_count % 20 == 0)
    
    effective_parent_id = request.parent_id if request.parent_id is not None else state.current_message_id
    user_message_content = request.message

    if request.action_id and request.action_id in ACTIONS_CONFIG:
        action_cfg = ACTIONS_CONFIG[request.action_id]
        user_message_content = action_cfg["message"]
        request.message = user_message_content
        
        stat_mod = action_cfg.get("stats", {})
        stats = dict(state.stats) if state.stats else {}
        stats["energy"] = max(0, min(100, stats.get("energy", 100) + stat_mod.get("energy", 0)))
        stats["hunger"] = max(0, min(100, stats.get("hunger", 0) + stat_mod.get("hunger", 0)))
        stats["happiness"] = max(0, min(100, stats.get("happiness", 100) + stat_mod.get("happiness", 0)))
        stats["social"] = max(0, min(100, stats.get("social", 100) + stat_mod.get("social", 0)))
        
        relationship = stats.get("relationship", {})
        if not isinstance(relationship, dict):
            relationship = {"score": 50}
        old_score = relationship.get("score", 50)
        relationship["score"] = max(0, min(100, old_score + stat_mod.get("relationship_score", 0)))
        stats["relationship"] = relationship
        
        state.stats = stats

    if not user_message_content and effective_parent_id:
        last_msg = db.query(MessageNode).filter(MessageNode.id == effective_parent_id).first()
        if last_msg and last_msg.role == "user":
            user_message_content = last_msg.content

    if request.message:
        user_msg = MessageNode(
            character_id=character.id, 
            user_id=user.id, 
            role="user", 
            content=request.message,
            parent_id=effective_parent_id,
            request_id=request_id
        )
        db.add(user_msg)
        db.flush()
        effective_parent_id = user_msg.id
        state.current_message_id = user_msg.id
        db.commit()

    history = []
    curr_id = effective_parent_id
    while curr_id and len(history) < 50:
        m = db.query(MessageNode).filter(MessageNode.id == curr_id, MessageNode.is_active == True).first()
        if not m: break
        history.append({"role": m.role, "content": m.content})
        curr_id = m.parent_id
    history.reverse()

    prompt = await brain.build_prompt(user_message_content or "", character, {"location": state.location, "mood": state.mood, "stats": state.stats, "active_summary": getattr(state, "active_summary", "")}, user=user, history=history[:-1] if request.message else history, db=db)

    # Extract config for dynamic LLM routing
    config = request.config or LLMConfig()
    
    from src.backend.db.models import SamplerPreset
    if config.preset_id:
        preset_obj = db.query(SamplerPreset).filter(SamplerPreset.id == config.preset_id).first()
    else:
        preset_obj = db.query(SamplerPreset).filter(SamplerPreset.is_default == True).first()
        
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

    async def generate():
        full_reply = ""
        try:
            async for token in llama.complete_stream(
                prompt, 
                url=config.base_url, 
                model=config.model_name,
                preset=preset_dict
            ):
                full_reply += token
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            if full_reply.strip():
                inner_db = SessionLocal()
                try:
                    inner_state = inner_db.query(AgentState).filter(AgentState.id == state.id).first()
                    variant_count = inner_db.query(MessageNode).filter(MessageNode.parent_id == effective_parent_id).count()
                    ai_msg = MessageNode(
                        character_id=character.id, 
                        user_id=user.id, 
                        role="assistant", 
                        content=full_reply,
                        parent_id=effective_parent_id,
                        variant_index=variant_count,
                        request_id=request_id
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
                        logger.warning(f"[{request_id}] AI Stream Response failed narrative formatting validation (RN-003).")

                    background_tasks.add_task(run_consciousness_layer, character.id, user_message_content or "", full_reply, force_reflect=force_reflect)
                    # Return full state for reactive HUD
                    updated_state = {
                        "location": inner_state.location,
                        "clothes": inner_state.clothes,
                        "mood": inner_state.mood,
                        "interaction_count": inner_state.interaction_count,
                        "stats": inner_state.stats
                    }
                    logger.info(f"[{request_id}] Stream Success: gen_len={len(full_reply)}")
                    yield f"data: {json.dumps({'done': True, 'request_id': request_id, 'state': updated_state, 'message_id': ai_msg.id})}\n\n"
                finally:
                    inner_db.close()
            else:
                yield f"data: {json.dumps({'done': True, 'request_id': request_id})}\n\n"
        except Exception as e:
            logger.error(f"[{request_id}] Stream Error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'request_id': request_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/characters/{character_id}/journal")
async def get_journal_entries(character_id: int, db: Session = Depends(get_db)):
    from src.backend.db.models import JournalEntry
    entries = db.query(JournalEntry).filter(JournalEntry.character_id == character_id).order_by(JournalEntry.timestamp.desc()).all()
    return [{
        "id": e.id,
        "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        "content": e.content,
        "summary": e.summary,
        "mood_at_time": e.mood_at_time,
        "relationship_score": e.relationship_score,
        "energy_level": e.energy_level
    } for e in entries]

def deactivate_subtree(node_id: int, db: Session):
    children = db.query(MessageNode).filter(MessageNode.parent_id == node_id).all()
    for child in children:
        child.is_active = False
        deactivate_subtree(child.id, db)

@router.put("/chat/message/{message_id}")
async def edit_message(message_id: int, req: MessageEditRequest, db: Session = Depends(get_db)):
    logger.info(f"Backend edit_message called: id={message_id}, content={req.content}")
    msg = db.query(MessageNode).filter(MessageNode.id == message_id, MessageNode.is_active == True).first()
    if not msg:
        logger.error(f"Backend edit_message: message {message_id} not found or inactive")
        raise HTTPException(status_code=404, detail="Message not found or inactive")
        
    msg.content = req.content
    
    # If a user message is edited, invalidate all subsequent assistant responses (and their subtrees)
    if msg.role == "user":
        logger.info(f"Backend edit_message: deactivating subtree for user message {message_id}")
        deactivate_subtree(msg.id, db)
        
        # Update current_message_id to the edited message so tree can resume from here
        state = db.query(AgentState).filter(AgentState.character_id == msg.character_id).first()
        if state:
            state.current_message_id = msg.id
            
    db.commit()
    logger.info(f"Backend edit_message: committed successfully for {message_id}")
    return {"status": "success", "message": "Message edited successfully"}

@router.delete("/chat/message/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(MessageNode).filter(MessageNode.id == message_id, MessageNode.is_active == True).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found or inactive")
        
    msg.is_active = False
    deactivate_subtree(msg.id, db)
    
    # Update current_message_id to parent if this was the current message
    state = db.query(AgentState).filter(AgentState.character_id == msg.character_id).first()
    if state and state.current_message_id == msg.id:
        state.current_message_id = msg.parent_id
        
    db.commit()
    return {"status": "success", "message": "Message deleted successfully"}
