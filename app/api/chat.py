import json
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
from app.db.models import AgentState, Character, User

router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)
reflector = Reflector(llm=llama)

def clean_json_response(content: str) -> Dict[str, Any]:
    """
    Cleans and parses the AI's JSON response, handling markdown and trailing noise.
    """
    content = content.strip()
    
    # Fast path: simple JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in markdown or noise
    import re
    # Match everything between the first { and the last }
    match = re.search(r"(\{.*\})", content, re.DOTALL)
    if match:
        json_str = match.group(1)
        
        # Try to fix common issues: unescaped newlines in strings, trailing commas
        # This is a basic attempt to find the balanced closing brace
        stack = 0
        end_idx = -1
        for i, char in enumerate(json_str):
            if char == '{': stack += 1
            elif char == '}':
                stack -= 1
                if stack == 0:
                    end_idx = i
                    break
        
        if end_idx != -1:
            json_str = json_str[:end_idx+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

    # If all else fails, return a fallback empty sequence with the raw content as speech
    return {"sequence": [{"type": "speech", "content": content}]}

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
        print(f"Error in consciousness layer: {e}")

# GBNF Grammar for the expected JSON structure
ACTION_GRAMMAR = r'''
root ::= "{" space "\"sequence\"" ":" space "[" space (block ("," space block)*)? space "]" space "}"
block ::= "{" space type_field "," space content_field space "}"
type_field ::= "\"type\"" ":" space ("\"thought\"" | "\"action\"" | "\"speech\"")
content_field ::= "\"content\"" ":" space string

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
            # Basic movement/mood parsing from action string if needed
            # For now, we just keep the existing logic if it was structured, 
            # but the new format is narrative.
            pass
    
    db.commit()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        # 0. Fetch User
        from app.db.models import User
        user = db.query(User).filter(User.is_active == True).first()
        if not user:
            # Create a default user if none exists
            user = User(name="User", gender="Unknown")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 1. Fetch Character and State
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

        # 2. Synchronize Physical State (Hunger, Energy, etc.)
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

        # 3. Assemble Prompt
        prompt = await brain.build_prompt(request.message, character, state_data, user=user)
        
        # 4. Request Inference
        result = await llama.complete(prompt, grammar=ACTION_GRAMMAR)
        content = result.get("content", "{}").strip()
        
        ai_data = clean_json_response(content)

        # 5. Process Autonomous Actions
        await process_ai_response(character.id, ai_data, db)

        # 6. Trigger Consciousness Layer in Background
        background_tasks.add_task(run_consciousness_layer, character.id, request.message, content)

        # Extract reply, thought, and actions from sequence
        sequence = ai_data.get("sequence", [])
        reply = " ".join([b["content"] for b in sequence if b.get("type") == "speech"])
        thought = " ".join([b["content"] for b in sequence if b.get("type") == "thought"])
        actions = [b["content"] for b in sequence if b.get("type") == "action"]

        return ChatResponse(
            reply=reply if reply else "...",
            thought=thought,
            actions=actions,
            sequence=sequence,
            stats=state.stats
        )
    except Exception as e:
        import logging
        logging.exception(f"CRITICAL ERROR in /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
