from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import Character, AgentState, Tag, JournalEntry
from src.backend.core.deps import brain

MAX_IMPORT_PNG_BYTES = (
    5 * 1024 * 1024
)  # character-card PNGs are a few KB of text; 5MB is generous

router = APIRouter()


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


class CharacterUpsert(BaseModel):
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
    avatar_url: Optional[str] = None


@router.post("/", response_model=CharacterResponse)
async def create_character(char: CharacterUpsert, db: Session = Depends(get_db)):
    new_char = Character(name=char.name, description=char.description)

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


@router.post("/import-png", response_model=CharacterResponse)
async def import_png(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read(MAX_IMPORT_PNG_BYTES + 1)
    if len(content) > MAX_IMPORT_PNG_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Character card exceeds the {MAX_IMPORT_PNG_BYTES // (1024 * 1024)}MB limit",
        )
    try:
        from src.backend.core.importer.png_parser import parse_png_character_card

        card = parse_png_character_card(content)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=f"Failed to parse PNG card: {str(e)}"
        )

    description = card.data.description
    if card.data.personality:
        description += "\n\n" + card.data.personality
    if card.data.scenario:
        description += "\n\nScenario: " + card.data.scenario

    # Combine system_prompt if any
    if card.data.system_prompt:
        description += "\n\nSystem: " + card.data.system_prompt

    new_char = Character(name=card.data.name, description=description)
    db.add(new_char)
    db.commit()
    db.refresh(new_char)

    # Save the original image
    import os

    os.makedirs("static/avatars", exist_ok=True)
    with open(f"static/avatars/{new_char.id}.png", "wb") as f:
        f.write(content)

    # Initialize state
    new_state = AgentState(character_id=new_char.id)
    if card.data.first_mes:
        new_state.mood = "Neutral (start of conversation)"
    db.add(new_state)
    db.commit()

    # Import Lorebook (character_book)
    if card.data.character_book and "entries" in card.data.character_book:
        from src.backend.db.models import LorebookEntry

        entries = card.data.character_book["entries"]
        for entry in entries:
            db_entry = LorebookEntry(
                character_id=new_char.id,
                keyword=",".join(entry.get("keys", [])),
                content=entry.get("content", ""),
                is_global=False,
            )
            db.add(db_entry)
        db.commit()

    db.refresh(new_char)
    new_char.avatar_url = f"/avatars/{new_char.id}.png"
    return new_char


@router.put("/{char_id}", response_model=CharacterResponse)
async def update_character(
    char_id: int, char: CharacterUpsert, db: Session = Depends(get_db)
):
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
    chars = db.query(Character).all()
    import os

    for char in chars:
        if os.path.exists(f"static/avatars/{char.id}.png"):
            char.avatar_url = f"/avatars/{char.id}.png"
    return chars


@router.get("/{char_id}", response_model=CharacterResponse)
def get_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    import os

    if os.path.exists(f"static/avatars/{char.id}.png"):
        char.avatar_url = f"/avatars/{char.id}.png"
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


def _apply_state_update(char: Character, state_data: StateUpdate, db: Session) -> None:
    state = char.state
    if not state:
        state = AgentState(character_id=char.id)
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


@router.put("/{char_id}/state", response_model=CharacterResponse)
def update_character_state(
    char_id: int, state_data: StateUpdate, db: Session = Depends(get_db)
):
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    _apply_state_update(char, state_data, db)
    try:
        db.commit()
    except StaleDataError:
        # Routine same-user contention (e.g. a stat button clicked while a
        # chat turn's decay commit is in flight) -- retry once against fresh
        # data instead of failing a low-stakes stat tweak outright. Re-query
        # rather than db.refresh(char): refresh requires the instance still
        # be attached the way it was before the rollback, which isn't
        # guaranteed.
        db.rollback()
        char = db.query(Character).filter(Character.id == char_id).first()
        _apply_state_update(char, state_data, db)
        db.commit()
    db.refresh(char)
    return char


@router.get("/{character_id}/journal")
async def get_journal_entries(character_id: int, db: Session = Depends(get_db)):
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.character_id == character_id)
        .order_by(JournalEntry.timestamp.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "content": e.content,
            "summary": e.summary,
            "mood_at_time": e.mood_at_time,
            "relationship_score": e.relationship_score,
            "energy_level": e.energy_level,
        }
        for e in entries
    ]
