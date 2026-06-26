from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import LorebookEntry
from src.backend.core.memory.vector_store import VectorStore
from src.backend.core.engine.llm import LlamaClient

router = APIRouter()

# Instantiate LLM and VectorStore
llama = LlamaClient()
vector_store = VectorStore(llm_client=llama)

class LoreCreate(BaseModel):
    keyword: str
    content: str
    character_id: Optional[int] = None
    is_global: bool = False

class LoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    keyword: str
    content: str
    character_id: Optional[int]
    is_global: bool

@router.post("/", response_model=LoreResponse)
async def create_lore_entry(entry: LoreCreate, db: Session = Depends(get_db)):
    db_entry = LorebookEntry(
        keyword=entry.keyword,
        content=entry.content,
        character_id=entry.character_id,
        is_global=entry.is_global
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Index in vector store for search/retrieval
    metadata = {
        "id": db_entry.id,
        "is_global": db_entry.is_global,
        "character_id": db_entry.character_id
    }
    await vector_store.add_lore(db_entry.keyword, db_entry.content, metadata=metadata)
    
    return db_entry

@router.get("/", response_model=List[LoreResponse])
def list_lore_entries(db: Session = Depends(get_db)):
    return db.query(LorebookEntry).all()

@router.delete("/{lore_id}")
def delete_lore_entry(lore_id: int, db: Session = Depends(get_db)):
    entry = db.query(LorebookEntry).filter(LorebookEntry.id == lore_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Lore entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Lore entry deleted"}
