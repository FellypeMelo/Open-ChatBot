import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.llm import LlamaClient
from app.core.bridge import Brain
from app.core.vector_store import VectorStore
from app.db.database import get_db
from app.db.models import AgentState

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

class ChatResponse(BaseModel):
    reply: str
    thought: str = ""

async def process_ai_response(agent_id: int, ai_output: Dict[str, Any], db: Session):
    """
    Processes the actions requested by the AI and updates the agent state.
    """
    agent = db.query(AgentState).filter(AgentState.id == agent_id).first()
    if not agent:
        return

    actions = ai_output.get("actions", [])
    for action in actions:
        action_type = action.get("type")
        if action_type == "move":
            agent.location = action.get("location", agent.location)
        elif action_type == "set_mood":
            agent.mood = action.get("mood", agent.mood)
    
    db.commit()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # For simplicity, assume we are always talking to agent with id=1
        agent = db.query(AgentState).filter(AgentState.id == 1).first()
        if not agent:
            # Create a default agent if not exists
            agent = AgentState(id=1, name="Gemi", location="Living Room", mood="Neutral")
            db.add(agent)
            db.commit()
            db.refresh(agent)

        state = {
            "name": agent.name,
            "location": agent.location,
            "mood": agent.mood,
            "stats": agent.stats
        }

        prompt = await brain.build_prompt(request.message, state)
        
        # Request completion with grammar
        result = await llama.complete(prompt, grammar=ACTION_GRAMMAR)
        content = result.get("content", "{}")
        
        try:
            ai_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if AI output is not valid JSON despite grammar
            return ChatResponse(reply=content)

        # Process actions
        await process_ai_response(agent.id, ai_data, db)

        return ChatResponse(
            reply=ai_data.get("message", "I didn't quite catch that."),
            thought=ai_data.get("thought", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
