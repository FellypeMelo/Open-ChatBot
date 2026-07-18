from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import Tag
from src.backend.api.common import get_or_404

router = APIRouter()


class TagCreate(BaseModel):
    label: str
    instruction: str


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    instruction: str


@router.post("/", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = Tag(**tag.model_dump())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_data: TagCreate, db: Session = Depends(get_db)):
    tag = get_or_404(db, Tag, tag_id, "Tag")
    for key, value in tag_data.model_dump().items():
        setattr(tag, key, value)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = get_or_404(db, Tag, tag_id, "Tag")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted"}
