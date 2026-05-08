from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Tag

router = APIRouter()

class TagCreate(BaseModel):
    label: str
    instruction: str

class TagResponse(BaseModel):
    id: int
    label: str
    instruction: str

    class Config:
        from_attributes = True

@router.post("/", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = Tag(label=tag.label, instruction=tag.instruction)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_data: TagCreate, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag.label = tag_data.label
    tag.instruction = tag_data.instruction
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted"}
