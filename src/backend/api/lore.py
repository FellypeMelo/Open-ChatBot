from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import LorebookEntry
from src.backend.core.deps import vector_store
from src.backend.api.common import get_or_404

router = APIRouter()


class LoreCreate(BaseModel):
    keyword: str
    keys: List[str] = []
    secondary_keys: List[str] = []
    content: str
    character_id: Optional[int] = None
    is_global: bool = False
    insertion_order: int = 100
    probability: int = 100
    scan_depth: int = 5
    is_constant: bool = False
    cooldown_turns: int = 0


class LoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword: str
    keys: List[str]
    secondary_keys: List[str]
    content: str
    character_id: Optional[int]
    is_global: bool
    insertion_order: int
    probability: int
    scan_depth: int
    is_constant: bool
    cooldown_turns: int


@router.post("/", response_model=LoreResponse)
async def create_lore_entry(entry: LoreCreate, db: Session = Depends(get_db)):
    db_entry = LorebookEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Index in vector store for search/retrieval
    metadata = {
        "id": db_entry.id,
        "is_global": db_entry.is_global,
        "character_id": db_entry.character_id,
    }
    await vector_store.add_lore(db_entry.keyword, db_entry.content, metadata=metadata)

    return db_entry


@router.get("/", response_model=List[LoreResponse])
def list_lore_entries(db: Session = Depends(get_db)):
    return db.query(LorebookEntry).all()


@router.delete("/{lore_id}")
def delete_lore_entry(lore_id: int, db: Session = Depends(get_db)):
    entry = get_or_404(db, LorebookEntry, lore_id, "Lore entry")
    db.delete(entry)
    db.commit()
    return {"message": "Lore entry deleted"}
