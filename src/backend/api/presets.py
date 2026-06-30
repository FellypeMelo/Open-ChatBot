from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from src.backend.db.database import get_db
from src.backend.db.models import SamplerPreset

router = APIRouter()

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
    presets = db.query(SamplerPreset).all()
    if not presets:
        # Create default presets
        p1 = SamplerPreset(
            name="Creative",
            is_default=True,
            temperature=1.05,
            min_p=0.03,
            top_k=0,
            top_p=1.0,
            repeat_penalty=1.0,
            dry_multiplier=0.8,
            dry_base=1.75,
            dry_range=4096,
            xtc_threshold=0.1,
            xtc_probability=0.4
        )
        p2 = SamplerPreset(
            name="Focused",
            is_default=False,
            temperature=0.7,
            min_p=0.05,
            top_k=0,
            top_p=1.0,
            repeat_penalty=1.0,
            dry_multiplier=0.6,
            dry_base=1.75,
            dry_range=2048,
            xtc_threshold=0.0,
            xtc_probability=0.0
        )
        db.add(p1)
        db.add(p2)
        db.commit()
        presets = db.query(SamplerPreset).all()
    return presets

@router.post("/", response_model=PresetSchema)
def create_preset(request: PresetCreateSchema, db: Session = Depends(get_db)):
    if request.is_default:
        db.query(SamplerPreset).update({SamplerPreset.is_default: False})
    
    preset = SamplerPreset(**request.model_dump())
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset

@router.put("/{preset_id}", response_model=PresetSchema)
def update_preset(preset_id: int, request: PresetCreateSchema, db: Session = Depends(get_db)):
    preset = db.query(SamplerPreset).filter(SamplerPreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    if request.is_default:
        db.query(SamplerPreset).update({SamplerPreset.is_default: False})
        
    for key, value in request.model_dump().items():
        setattr(preset, key, value)
        
    db.commit()
    db.refresh(preset)
    return preset

@router.delete("/{preset_id}")
def delete_preset(preset_id: int, db: Session = Depends(get_db)):
    preset = db.query(SamplerPreset).filter(SamplerPreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    if preset.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete the default preset")
        
    db.delete(preset)
    db.commit()
    return {"status": "deleted"}
