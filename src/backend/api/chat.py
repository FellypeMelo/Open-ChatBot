import json
import logging
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from src.backend.core.engine.llm import LlamaClient
from src.backend.core.orchestration.bridge import Brain
from src.backend.core.memory.vector_store import VectorStore
from src.backend.core.engine.engine import update_needs, evolve_character
from src.backend.db.database import get_db, SessionLocal
from src.backend.db.models import AgentState, Character, User, MessageNode
from src.backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)

async def run_consciousness_layer(character_id: int, user_message: str, ai_response: str):
    """Background task for memory and evolution."""
    try:
        db = SessionLocal()
        try:
            # 1. Store memory
            await vector_store.add_memory(f"User: {user_message}\nAI: {ai_response}", metadata={"character_id": character_id})
            
            # 2. Reflect & Evolve
            messages = [{"role": "user", "content": user_message}, {"role": "assistant", "content": ai_response}]
            reflection = await brain.reflect(messages)
            evolve_character(db, character_id, reflection)
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Consciousness layer error: {e}")

class ChatRequest(BaseModel):
    message: Optional[str] = None
    character_id: int = 1
    parent_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    stats: Dict[str, Any] = {}
    latency: Dict[str, float] = {}

@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(character_id: int, db: Session = Depends(get_db)):
    messages = db.query(MessageNode).filter(MessageNode.character_id == character_id).order_by(MessageNode.timestamp.desc()).limit(100).all()
    return [{
        "id": m.id,
        "parent_id": m.parent_id,
        "role": m.role,
        "content": m.content,
        "variant_index": m.variant_index,
        "timestamp": m.timestamp
    } for m in reversed(messages)]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start = time.perf_counter()
    try:
        user = db.query(User).filter(User.is_active == True).first() or User(name="User", gender="Unknown")
        if not user.id: db.add(user); db.flush()

        character = db.query(Character).filter(Character.id == request.character_id).first() or Character.get_default(db)
        state = character.state or AgentState(character_id=character.id)
        if not state.id: db.add(state); db.flush()

        state.stats = update_needs(state.stats, datetime.now())
        
        effective_parent_id = request.parent_id if request.parent_id is not None else state.current_message_id
        user_message_content = request.message

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
                parent_id=effective_parent_id
            )
            db.add(user_msg)
            db.flush()
            effective_parent_id = user_msg.id
            state.current_message_id = user_msg.id

        history = []
        curr_id = effective_parent_id
        while curr_id and len(history) < 11:
            m = db.query(MessageNode).filter(MessageNode.id == curr_id).first()
            if not m: break
            history.append({"role": m.role, "content": m.content})
            curr_id = m.parent_id
        history.reverse()

        prompt = await brain.build_prompt(user_message_content or "", character, {"location": state.location, "mood": state.mood, "stats": state.stats}, user=user, history=history[:-1] if request.message else history)
        
        result = await llama.complete(prompt)
        reply = result.get("content", "...").strip()

        variant_count = db.query(MessageNode).filter(MessageNode.parent_id == effective_parent_id).count()
        ai_msg = MessageNode(
            character_id=character.id, 
            user_id=user.id, 
            role="assistant", 
            content=reply,
            parent_id=effective_parent_id,
            variant_index=variant_count
        )
        db.add(ai_msg)
        db.flush()
        state.current_message_id = ai_msg.id
        db.commit()
        
        background_tasks.add_task(run_consciousness_layer, character.id, user_message_content or "", reply)

        latency = {"total": time.perf_counter() - start} if settings.DEBUG_LATENCY else {}
        return ChatResponse(reply=reply, stats=state.stats, latency=latency)
    except Exception as e:
        db.rollback()
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.is_active == True).first() or User(name="User", gender="Unknown")
    if not user.id: db.add(user); db.flush()

    character = db.query(Character).filter(Character.id == request.character_id).first() or Character.get_default(db)
    state = character.state or AgentState(character_id=character.id)
    if not state.id: db.add(state); db.flush()

    state.stats = update_needs(state.stats, datetime.now())
    
    effective_parent_id = request.parent_id if request.parent_id is not None else state.current_message_id
    user_message_content = request.message

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
            parent_id=effective_parent_id
        )
        db.add(user_msg)
        db.flush()
        effective_parent_id = user_msg.id
        state.current_message_id = user_msg.id
        db.commit()

    history = []
    curr_id = effective_parent_id
    while curr_id and len(history) < 11:
        m = db.query(MessageNode).filter(MessageNode.id == curr_id).first()
        if not m: break
        history.append({"role": m.role, "content": m.content})
        curr_id = m.parent_id
    history.reverse()

    prompt = await brain.build_prompt(user_message_content or "", character, {"location": state.location, "mood": state.mood, "stats": state.stats}, user=user, history=history[:-1] if request.message else history)

    async def generate():
        full_reply = ""
        async for token in llama.complete_stream(prompt):
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
                    variant_index=variant_count
                )
                inner_db.add(ai_msg)
                inner_db.flush()
                if inner_state:
                    inner_state.current_message_id = ai_msg.id
                inner_db.commit()
                background_tasks.add_task(run_consciousness_layer, character.id, user_message_content or "", full_reply)
                
                inner_char = inner_db.query(Character).filter(Character.id == character.id).first()
                final_stats = inner_char.state.stats if inner_char and inner_char.state else {}
                yield f"data: {json.dumps({'done': True, 'stats': final_stats, 'message_id': ai_msg.id})}\n\n"
            finally:
                inner_db.close()
        else:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
