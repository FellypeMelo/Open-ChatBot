import json
import logging
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.llm import LlamaClient
from app.core.bridge import Brain
from app.core.vector_store import VectorStore
from app.core.reflector import Reflector
from app.core.evolution import EvolutionManager
from app.db.database import get_db
from app.db.models import AgentState, Character, User, Message
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)
reflector = Reflector(llm=llama)

def clean_json_response(content: str) -> Dict[str, Any]:
    """
    Cleans and parses the AI's JSON response, handling markdown and trailing noise.
    Finds the LAST valid JSON block — the model often outputs garbage before the real response.
    """
    content = content.strip()

    # Fast path: simple JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Find ALL balanced JSON blocks, return the last valid one
    import re
    valid_blocks = []
    search_start = 0
    while True:
        start_idx = content.find('{', search_start)
        if start_idx == -1:
            break
        stack = 0
        for i in range(start_idx, len(content)):
            if content[i] == '{':
                stack += 1
            elif content[i] == '}':
                stack -= 1
                if stack == 0:
                    json_str = content[start_idx : i + 1]
                    try:
                        parsed = json.loads(json_str)
                        valid_blocks.append(parsed)
                    except json.JSONDecodeError:
                        fixed_json = re.sub(r'(?<=[:[,])\s*"(.*?)"', lambda m: m.group(0).replace('\n', '\\n'), json_str)
                        try:
                            parsed = json.loads(fixed_json)
                            valid_blocks.append(parsed)
                        except:
                            pass
                    search_start = i + 1
                    break
        else:
            break

    if valid_blocks:
        return valid_blocks[-1]

    return {"reply": content}


async def run_consciousness_layer(character_id: int, user_message: str, ai_response: str):
    """
    Background task to handle memory storage and character evolution.
    """
    try:
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            # 1. Store interaction in memory
            memory_text = f"User: {user_message}\nAI: {ai_response}"
            await vector_store.add_memory(memory_text, metadata={"character_id": character_id})
            
            # 2. Trigger Reflection
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ]
            reflection = await reflector.reflect(messages)
            
            # 3. Evolve Character
            evolution = EvolutionManager(db)
            evolution.evolve(character_id, reflection)
        finally:
            db.close()
        
    except Exception as e:
        logger.exception(f"Error in consciousness layer: {e}")

# GBNF Grammar for the expected JSON structure
ACTION_GRAMMAR = r'''
root ::= "{" space "\"sequence\"" ":" space "[" space (block ("," space block)*)? space "]" space "}"
block ::= "{" space "\"type\"" ":" space ("\"thought\"" | "\"action\"" | "\"speech\"") "," space "\"content\"" ":" space string space "}"
string ::= "\"" ([^"\\] | "\\" ["\\/bfnrt] | "\\u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])* "\""
space ::= [ \t\n\r]*
'''

class ChatRequest(BaseModel):
    message: str
    character_id: int = 1

class ChatResponse(BaseModel):
    reply: str
    thought: str = ""
    actions: List[str] = []
    sequence: List[Dict[str, str]] = []
    stats: Dict[str, Any] = {}
    latency: Dict[str, float] = {}

@router.get("/history/{character_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(character_id: int, db: Session = Depends(get_db)):
    """
    Fetches the last 50 messages for a character.
    """
    from app.db.models import Message
    messages = db.query(Message).filter(Message.character_id == character_id).order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse() # Back to chronological order
    
    history = []
    for msg in messages:
        content = msg.content
        sequence = []
        # Try to parse content as JSON sequence if it's from assistant
        if msg.role == "assistant":
            try:
                data = json.loads(content)
                sequence = data.get("sequence", [])
                # If sequence is found, content should be the speech parts
                if sequence:
                    content = " ".join([b["content"] for b in sequence if b.get("type") == "speech"])
            except:
                pass
        
        history.append({
            "role": msg.role,
            "content": content,
            "sequence": sequence,
            "timestamp": msg.timestamp
        })
    return history

async def process_ai_response(agent_id: int, ai_output: Dict[str, Any], db: Session):
    """
    Processes the actions requested by the AI and updates the agent state.
    """
    agent = db.query(AgentState).filter(AgentState.character_id == agent_id).first()
    if not agent:
        return

    # In the new sequence format, actions are in the sequence list
    sequence = ai_output.get("sequence", [])
    for block in sequence:
        if block.get("type") == "action":
            content = block.get("content", "")
            pass
    
    db.commit()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start_total = time.perf_counter()
    try:
        # 0. Fetch User
        t0 = time.perf_counter()
        from app.db.models import User
        user = db.query(User).filter(User.is_active == True).first()
        if not user:
            # Create a default user if none exists
            user = User(name="User", gender="Unknown")
            db.add(user)
            db.commit()
            db.refresh(user)
        dur_user = time.perf_counter() - t0

        # Save user message to history
        user_msg = Message(
            character_id=request.character_id,
            user_id=user.id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        db.commit()

        # Fetch recent history for prompt context (last 10 messages)
        # Exclude the message we just saved
        history = db.query(Message).filter(
            Message.character_id == request.character_id,
            Message.id != user_msg.id
        ).order_by(Message.timestamp.desc()).limit(10).all()
        history.reverse() # Back to chronological order

        # 1. Fetch Character and State
        t1 = time.perf_counter()
        character = db.query(Character).filter(Character.id == request.character_id).first()
        if not character:
            # Create a default character (Gemi) if none exists
            character = Character(
                id=1, 
                name="Gemi", 
                description="A playful and feisty entity who enjoys testing boundaries."
            )
            db.add(character)
            db.commit()
            db.refresh(character)
            
            # Create default state
            state = AgentState(character_id=character.id)
            db.add(state)
            db.commit()
            db.refresh(state)
        else:
            state = character.state
            if not state:
                state = AgentState(character_id=character.id)
                db.add(state)
                db.commit()
                db.refresh(state)
        dur_char = time.perf_counter() - t1

        # 2. Synchronize Physical State (Hunger, Energy, etc.)
        t2 = time.perf_counter()
        from app.core.world import WorldEngine
        from app.core.evolution import ensure_stats_integrity
        world = WorldEngine()
        
        # Ensure stats integrity before processing
        state.stats = ensure_stats_integrity(state.stats)
        state.stats = world.update_needs(state.stats, datetime.now())
        db.commit()

        state_data = {
            "location": state.location,
            "mood": state.mood,
            "clothes": state.clothes,
            "stats": state.stats
        }
        dur_world = time.perf_counter() - t2

        # 3. Assemble Prompt
        t3 = time.perf_counter()
        prompt = await brain.build_prompt(request.message, character, state_data, user=user, history=history)
        dur_brain = time.perf_counter() - t3
        
        # 4. Request Inference
        t4 = time.perf_counter()
        result = await llama.complete(prompt, grammar=None)
        dur_llm = time.perf_counter() - t4
        
        content = result.get("content", "").strip()
        logger.debug(f"RAW LLM CONTENT: {content}")
        
        # Save AI response to history
        ai_msg = Message(
            character_id=character.id,
            user_id=user.id,
            role="assistant",
            content=content # Store raw JSON sequence
        )
        db.add(ai_msg)
        db.commit()

        t5 = time.perf_counter()
        ai_data = clean_json_response(content)
        logger.debug(f"PARSED AI DATA: {ai_data}")

        # 5. Process Autonomous Actions
        await process_ai_response(character.id, ai_data, db)
        dur_process = time.perf_counter() - t5

        # 6. Trigger Consciousness Layer in Background
        background_tasks.add_task(run_consciousness_layer, character.id, request.message, content)

        # Extract reply, thought, and actions from sequence
        sequence = ai_data.get("sequence", [])
        
        reply = " ".join([b["content"] for b in sequence if b.get("type") == "speech"])
        thought = " ".join([b["content"] for b in sequence if b.get("type") == "thought"])
        actions = [b["content"] for b in sequence if b.get("type") == "action"]

        # Fallback: if no structured reply, use raw LLM reply field
        if not reply:
            reply = ai_data.get("reply", "")

        total_dur = time.perf_counter() - start_total
        latency_map = {}
        if settings.DEBUG_LATENCY:
            latency_map = {
                "user": dur_user,
                "char": dur_char,
                "world": dur_world,
                "brain": dur_brain,
                "llm": dur_llm,
                "process": dur_process,
                "total": total_dur
            }

        logger.debug(
            f"LATENCY BREAKDOWN [{request.character_id}]: "
            f"User: {dur_user:.3f}s | "
            f"Char: {dur_char:.3f}s | "
            f"World: {dur_world:.3f}s | "
            f"Brain(RAG): {dur_brain:.3f}s | "
            f"LLM: {dur_llm:.3f}s | "
            f"Process: {dur_process:.3f}s | "
            f"TOTAL: {total_dur:.3f}s"
        )

        logger.debug(f"ChatResponse: {reply=}, {thought=}, {actions=}, {sequence=}")

        return ChatResponse(
            reply=reply if reply else "...",
            thought=thought,
            actions=actions,
            sequence=sequence,
            stats=state.stats,
            latency=latency_map
        )
    except Exception as e:
        import logging
        logging.exception(f"CRITICAL ERROR in /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
