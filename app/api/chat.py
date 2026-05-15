import json
import logging
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.llm import LlamaClient
from app.core.bridge import Brain
from app.core.vector_store import VectorStore
from app.core.engine import update_needs, evolve_character
from app.db.database import get_db, SessionLocal
from app.db.models import AgentState, Character, User, Message
from app.core.config import settings

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
    message: str
    character_id: int = 1

class ChatResponse(BaseModel):
    reply: str
    stats: Dict[str, Any] = {}
    latency: Dict[str, float] = {}

@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(character_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.character_id == character_id).order_by(Message.timestamp.desc()).limit(50).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in reversed(messages)]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start = time.perf_counter()
    try:
        # 1. Fetch Entities (using defaults if needed)
        user = db.query(User).filter(User.is_active == True).first() or User(name="User", gender="Unknown")
        if not user.id: db.add(user); db.flush()

        character = db.query(Character).filter(Character.id == request.character_id).first() or Character.get_default(db)
        if not character.id: db.add(character); db.flush()
        
        state = character.state or AgentState(character_id=character.id)
        if not state.id: db.add(state); db.flush()

        # 2. Update Physical Needs & History
        state.stats = update_needs(state.stats, datetime.now())
        db.add(Message(character_id=character.id, user_id=user.id, role="user", content=request.message))

        # 3. Assemble Context & History
        # Get history (excluding current user message)
        hist_msgs = db.query(Message).filter(Message.character_id == character.id).order_by(Message.timestamp.desc()).limit(11).all()
        history = list(reversed(hist_msgs[1:]))

        prompt = await brain.build_prompt(request.message, character, {"location": state.location, "mood": state.mood, "stats": state.stats}, user=user, history=history)
        
        # 4. LLM Completion
        result = await llama.complete(prompt)
        reply = result.get("content", "...").strip()

        # 5. Persist AI Response
        db.add(Message(character_id=character.id, user_id=user.id, role="assistant", content=reply))
        db.commit() # Single commit for all changes
        
        background_tasks.add_task(run_consciousness_layer, character.id, request.message, reply)

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

    character = db.query(Character).filter(Character.id == request.character_id).first() or Character(name="Gemi", description="Playful entity.")
    if not character.id: db.add(character); db.flush()

    state = character.state or AgentState(character_id=character.id)
    if not state.id: db.add(state); db.flush()

    state.stats = update_needs(state.stats, datetime.now())
    db.add(Message(character_id=character.id, user_id=user.id, role="user", content=request.message))
    db.commit()

    history = db.query(Message).filter(Message.character_id == character.id).order_by(Message.timestamp.desc()).limit(11).all()
    prompt = await brain.build_prompt(request.message, character, {"location": state.location, "mood": state.mood, "stats": state.stats}, user=user, history=reversed(history[1:]))

    async def generate():
        full_reply = ""
        async for token in llama.complete_stream(prompt):
            full_reply += token
            yield f"data: {json.dumps({'token': token})}\n\n"
        
        if full_reply.strip():
            inner_db = SessionLocal()
            try:
                inner_db.add(Message(character_id=character.id, user_id=user.id, role="assistant", content=full_reply))
                inner_db.commit()
                background_tasks.add_task(run_consciousness_layer, character.id, request.message, full_reply)
                
                # Refresh character to get updated stats (from the consciousness layer if it ran sync, 
                # but usually we want the current physical drain state at minimum)
                inner_db.refresh(character)
                final_stats = character.state.stats if character.state else {}
                yield f"data: {json.dumps({'done': True, 'stats': final_stats})}\n\n"
            finally:
                inner_db.close()
        else:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
