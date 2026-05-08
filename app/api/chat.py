import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.llm import LlamaClient
from app.core.bridge import Brain
from app.core.vector_store import VectorStore
from app.db.database import get_db
from app.db.models import AgentState, Character

router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)

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
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        print(f"Chat request for character {request.character_id}")
        
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
            print("Creating default character")
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
            print(f"Found character {character.name}")
            state = character.state
            if not state:
                print("Creating default state for existing character")
                state = AgentState(character_id=character.id)
                db.add(state)
                db.commit()
                db.refresh(state)

        # 2. Synchronize Physical State (Hunger, Energy, etc.)
        from app.core.world import WorldEngine
        from datetime import datetime
        print("Updating needs...")
        world = WorldEngine()
        state.stats = world.update_needs(state.stats, datetime.now())
        db.commit()

        state_data = {
            "location": state.location,
            "mood": state.mood,
            "clothes": state.clothes,
            "stats": state.stats
        }

        # 3. Assemble Prompt
        print("Building prompt...")
        prompt = await brain.build_prompt(request.message, character, state_data, user=user)
        
        # 4. Request Inference
        print("Requesting inference...")
        result = await llama.complete(prompt, grammar=ACTION_GRAMMAR)
        content = result.get("content", "{}").strip()
        print(f"AI Output: {content}")
        
        try:
            ai_data = json.loads(content)
        except json.JSONDecodeError:
            # Try harder to find valid JSON
            import re
            # Find all potential JSON objects
            json_blocks = re.findall(r"\{.*\}", content, re.DOTALL)
            ai_data = None
            if json_blocks:
                # Try from the largest to smallest or first to last
                for block in json_blocks:
                    try:
                        # Clean up common markdown mess
                        cleaned = block.strip()
                        # If it ends with extra braces or markdown, try to truncate
                        # This is a bit hacky but AI sometimes outputs: { ... } extra text
                        # We'll try to find the balancing brace
                        stack = 0
                        end_idx = -1
                        for i, char in enumerate(cleaned):
                            if char == '{': stack += 1
                            elif char == '}':
                                stack -= 1
                                if stack == 0:
                                    end_idx = i
                                    break
                        if end_idx != -1:
                            cleaned = cleaned[:end_idx+1]
                        
                        ai_data = json.loads(cleaned)
                        if ai_data: break
                    except:
                        continue
            
            if not ai_data:
                print(f"FAILED to parse AI output as JSON: {content}")
                return ChatResponse(reply=content, stats=state.stats)

        # 5. Process Autonomous Actions
        print("Processing AI response...")
        await process_ai_response(character.id, ai_data, db)

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
        print(f"CRITICAL ERROR in /chat: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
