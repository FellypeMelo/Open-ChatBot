"""Small shared helpers for the FastAPI routers."""

from typing import Type, TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

T = TypeVar("T")


def get_or_404(db: Session, model: Type[T], entity_id: int, name: str) -> T:
    """Fetch a row by primary key or raise a 404 whose detail is '<name> not found'."""
    entity = db.query(model).filter(model.id == entity_id).first()
    if entity is None:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return entity
