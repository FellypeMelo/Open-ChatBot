from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.backend.db.database import get_db
from src.backend.db.models import User

router = APIRouter()


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gender: str
    is_active: bool
    persona_description: str = ""
    appearance: str = ""


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    persona_description: Optional[str] = None
    appearance: Optional[str] = None


@router.get("/me", response_model=UserSchema)
def get_me(db: Session = Depends(get_db)):
    user = User.get_or_create_active(db)
    db.commit()
    db.refresh(user)
    return user


@router.post("/me", response_model=UserSchema)
def update_me(request: UserUpdateSchema, db: Session = Depends(get_db)):
    user = User.get_or_create_active(db)

    # Only overwrite fields the caller actually sent (None means "leave as-is").
    for key, value in request.model_dump(exclude_none=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user
