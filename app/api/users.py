from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.db.models import User

router = APIRouter()

class UserSchema(BaseModel):
    id: int
    name: str
    gender: str
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None

@router.get("/me", response_model=UserSchema)
def get_me(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.is_active == True).first()
    if not user:
        # Create default user if none exists
        user = User(name="User", gender="Male", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/me", response_model=UserSchema)
def update_me(request: UserUpdateSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.is_active == True).first()
    if not user:
        user = User(name="User", gender="Male", is_active=True)
        db.add(user)
    
    if request.name is not None:
        user.name = request.name
    if request.gender is not None:
        user.gender = request.gender
    
    db.commit()
    db.refresh(user)
    return user
