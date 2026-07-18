from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from src.backend.db.database import get_db
from src.backend.db.models import SamplerPreset
from src.backend.api.common import get_or_404

router = APIRouter()


def _clear_default_flag(db: Session) -> None:
    """Clear is_default on every preset so a new default can be set uniquely."""
    db.query(SamplerPreset).update({SamplerPreset.is_default: False})


class PresetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    is_default: bool
    temperature: float
    min_p: float
    top_k: int
    top_p: float
    repeat_penalty: float
    dry_multiplier: float
    dry_base: float
    dry_range: int
    xtc_threshold: float
    xtc_probability: float


class PresetCreateSchema(BaseModel):
    name: str
    is_default: Optional[bool] = False
    temperature: Optional[float] = 1.0
    min_p: Optional[float] = 0.05
    top_k: Optional[int] = 0
    top_p: Optional[float] = 1.0
    repeat_penalty: Optional[float] = 1.0
    dry_multiplier: Optional[float] = 0.0
    dry_base: Optional[float] = 1.75
    dry_range: Optional[int] = 2048
    xtc_threshold: Optional[float] = 0.0
    xtc_probability: Optional[float] = 0.0


@router.get("/", response_model=List[PresetSchema])
def get_presets(db: Session = Depends(get_db)):
    # Default presets are seeded once at app startup (see database._seed_default_presets),
    # not lazily here -- this endpoint just reads what already exists.
    return db.query(SamplerPreset).all()


@router.post("/", response_model=PresetSchema)
def create_preset(request: PresetCreateSchema, db: Session = Depends(get_db)):
    if request.is_default:
        _clear_default_flag(db)

    preset = SamplerPreset(**request.model_dump())
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


@router.put("/{preset_id}", response_model=PresetSchema)
def update_preset(
    preset_id: int, request: PresetCreateSchema, db: Session = Depends(get_db)
):
    preset = get_or_404(db, SamplerPreset, preset_id, "Preset")

    if request.is_default:
        _clear_default_flag(db)

    # exclude_unset: only overwrite fields the caller actually sent, so a
    # partial PUT doesn't silently reset every omitted field back to
    # PresetCreateSchema's defaults (frontend always sends the full object
    # today, but this makes the endpoint correct regardless of caller).
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(preset, key, value)

    db.commit()
    db.refresh(preset)
    return preset


@router.delete("/{preset_id}")
def delete_preset(preset_id: int, db: Session = Depends(get_db)):
    preset = get_or_404(db, SamplerPreset, preset_id, "Preset")

    if preset.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete the default preset")

    db.delete(preset)
    db.commit()
    return {"status": "deleted"}
