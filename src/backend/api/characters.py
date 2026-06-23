from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import Character, AgentState, Tag
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.orchestration.bridge import Brain
from src.backend.core.memory.vector_store import VectorStore

router = APIRouter()
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)
brain = Brain(vector_store=vector_store)

class DescriptionRequest(BaseModel):
    description: str

@router.post("/auto-tag", response_model=List[int])
async def auto_tag_character(req: DescriptionRequest, db: Session = Depends(get_db)):
    return await brain.suggest_tags(req.description, db)

class TagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    label: str
    instruction: str

class StateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    location: str
    mood: str
    clothes: str
    stats: dict

class CharacterCreate(BaseModel):
    name: str
    description: str
    tag_ids: List[int] = []

class CharacterUpdate(BaseModel):
    name: str
    description: str
    tag_ids: List[int] = []

class CharacterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
    is_active: bool
    tags: List[TagSchema] = []
    state: Optional[StateResponse] = None

@router.post("/", response_model=CharacterResponse)
def create_character(char: CharacterCreate, db: Session = Depends(get_db)):
    new_char = Character(
        name=char.name,
        description=char.description
    )
    
    # Associate tags
    if char.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(char.tag_ids)).all()
        new_char.tags = tags
    
    db.add(new_char)
    db.commit()
    db.refresh(new_char)
    
    # Initialize state
    new_state = AgentState(character_id=new_char.id)
    db.add(new_state)
    db.commit()
    
    return new_char

@router.put("/{char_id}", response_model=CharacterResponse)
def update_character(char_id: int, char: CharacterUpdate, db: Session = Depends(get_db)):
    existing = db.query(Character).filter(Character.id == char_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Character not found")
    
    existing.name = char.name
    existing.description = char.description
    
    if char.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(char.tag_ids)).all()
        existing.tags = tags
    
    db.commit()
    db.refresh(existing)
    return existing

@router.get("/", response_model=List[CharacterResponse])
def list_characters(db: Session = Depends(get_db)):
    return db.query(Character).all()

@router.get("/{char_id}", response_model=CharacterResponse)
def get_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char

@router.delete("/{char_id}")
def delete_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(char)
    db.commit()
    return {"message": "Character deleted"}

class StatsUpdate(BaseModel):
    energy: Optional[int] = None
    hunger: Optional[int] = None
    happiness: Optional[int] = None
    social: Optional[int] = None
    is_sleeping: Optional[bool] = None
    relationship_score: Optional[int] = None

class StateUpdate(BaseModel):
    location: Optional[str] = None
    mood: Optional[str] = None
    clothes: Optional[str] = None
    stats: Optional[StatsUpdate] = None

@router.put("/{char_id}/state", response_model=CharacterResponse)
def update_character_state(char_id: int, state_data: StateUpdate, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
        
    state = char.state
    if not state:
        state = AgentState(character_id=char_id)
        db.add(state)
        
    if state_data.location is not None:
        state.location = state_data.location
    if state_data.mood is not None:
        state.mood = state_data.mood
    if state_data.clothes is not None:
        state.clothes = state_data.clothes
        
    if state_data.stats is not None:
        current_stats = dict(state.stats) if state.stats else {}
        if state_data.stats.energy is not None:
            current_stats["energy"] = max(0, min(100, state_data.stats.energy))
        if state_data.stats.hunger is not None:
            current_stats["hunger"] = max(0, min(100, state_data.stats.hunger))
        if state_data.stats.happiness is not None:
            current_stats["happiness"] = max(0, min(100, state_data.stats.happiness))
        if state_data.stats.social is not None:
            current_stats["social"] = max(0, min(100, state_data.stats.social))
        if state_data.stats.is_sleeping is not None:
            current_stats["is_sleeping"] = state_data.stats.is_sleeping
        if state_data.stats.relationship_score is not None:
            rel = current_stats.get("relationship", {})
            if not isinstance(rel, dict):
                rel = {"score": 50}
            rel["score"] = max(0, min(100, state_data.stats.relationship_score))
            current_stats["relationship"] = rel
            
        state.stats = current_stats
        
    db.commit()
    db.refresh(char)
    return char
