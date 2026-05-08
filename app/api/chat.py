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
root ::= object
object ::= "{" space (thought_item ",")? space (actions_item ",")? space message_item space "}"
thought_item ::= "\"thought\"" ":" space string
actions_item ::= "\"actions\"" ":" space "[" space (action ("," space action)*)? space "]"
message_item ::= "\"message\"" ":" space string

action ::= "{" space type_item "," space payload_item space "}"
type_item ::= "\"type\"" ":" space ("\"move\"" | "\"set_mood\"")
payload_item ::= ("\"location\"" ":" space string) | ("\"mood\"" ":" space string)

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

async def process_ai_response(agent_id: int, ai_output: Dict[str, Any], db: Session):
    """
    Processes the actions requested by the AI and updates the agent state.
    """
    agent = db.query(AgentState).filter(AgentState.character_id == agent_id).first()
    if not agent:
        return

    actions = ai_output.get("actions", [])
    for action in actions:
        # Action can be a string (from Master Prompt Actions Field) or a structured dict
        # The Master Prompt says "ACTIONS FIELD: Physical behavior, body language, movement..."
        # But our logic previously used structured dicts.
        # Let's keep it flexible: if it's a dict, parse it. If it's a string, it's body language (ignore for DB logic).
        if isinstance(action, dict):
            action_type = action.get("type")
            if action_type == "move":
                agent.location = action.get("location", agent.location)
            elif action_type == "set_mood":
                agent.mood = action.get("mood", agent.mood)
    
    db.commit()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
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

        # 2. Synchronize Physical State (Hunger, Energy, etc.)
        from app.core.world import WorldEngine
        from datetime import datetime
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
        prompt = await brain.build_prompt(request.message, character, state_data)
        
        # 4. Request Inference
        result = await llama.complete(prompt, grammar=ACTION_GRAMMAR)
        content = result.get("content", "{}")
        
        try:
            ai_data = json.loads(content)
        except json.JSONDecodeError:
            return ChatResponse(reply=content)

        # 5. Process Autonomous Actions
        await process_ai_response(character.id, ai_data, db)

        return ChatResponse(
            reply=ai_data.get("message", "I didn't quite catch that."),
            thought=ai_data.get("thought", ""),
            actions=ai_data.get("actions", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
