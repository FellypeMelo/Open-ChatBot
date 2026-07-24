from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.backend.db.database import get_db
from src.backend.db.models import (
    Character,
    AgentState,
    Tag,
    JournalEntry,
    MessageNode,
    LorebookEntry,
    Chat,
    User,
)
from src.backend.api.chat import seed_initial_chat
from src.backend.core.deps import brain, vector_store
from src.backend.core.engine.engine import clamp_stat, DEFAULT_RELATIONSHIP_SCORE
from src.backend.api.common import get_or_404

MAX_IMPORT_PNG_BYTES = (
    5 * 1024 * 1024
)  # character-card PNGs are a few KB of text; 5MB is generous

# Longest side (px) a stored avatar is downscaled to on upload. The character
# grid renders avatars at only 40x40 (CharactersView.tsx), but the Create/Edit
# Character modal's own preview renders the *stored* avatar_url up to a 200px
# desktop column (aspect-square) and, stacked full-width below the md
# breakpoint on mobile, up to roughly 350-400px -- so 512 gives the largest
# real on-screen use comfortable headroom for ~2x/3x pixel-density screens
# without keeping the up-to-5MB full-resolution original on disk.
AVATAR_MAX_DIMENSION = 512

# Upper bound on a source image's declared pixel count (width * height)
# accepted for avatar processing, checked from the header alone -- before
# Pillow decodes any pixel data -- so a crafted upload never gets the chance
# to be fully decoded server-side. 50 megapixels is generous for any real
# photo (a 48MP phone high-res shot is ~48,000,000) while sitting well below
# Pillow's own DecompressionBombWarning threshold (~89M pixels, which it
# only warns on, not blocks) and far below its hard DecompressionBombError
# threshold (~179M pixels). Without this pre-check, a pixel count between
# those two Pillow thresholds decodes fully (real memory cost, no error to
# even catch), and a pixel count above the hard threshold raises
# DecompressionBombError from inside Image.open() itself, which
# _save_avatar_image's broad except-fallback below would otherwise swallow
# and write the still-undecoded original to disk completely unresized --
# exactly the input the resize feature exists to catch.
AVATAR_MAX_SOURCE_PIXELS = 50_000_000

router = APIRouter()


def _reject_oversized_avatar(content: bytes) -> None:
    """Raise 413 if `content` is an image whose declared dimensions exceed
    AVATAR_MAX_SOURCE_PIXELS. Must run before any DB writes and before
    _save_avatar_image's decode step, so a pathological upload is rejected
    outright instead of being fully decoded or written to disk unresized.

    Bytes that aren't a decodable image at all are left alone here --
    _save_avatar_image's existing raw-bytes fallback is what handles those,
    and there's no pixel count to bound in that case."""
    from io import BytesIO
    from PIL import Image

    try:
        with Image.open(BytesIO(content)) as img:
            width, height = img.size
    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the maximum allowed pixel dimensions",
        )
    except Exception:
        return

    if width * height > AVATAR_MAX_SOURCE_PIXELS:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Image dimensions ({width}x{height}) exceed the "
                f"{AVATAR_MAX_SOURCE_PIXELS // 1_000_000}-megapixel limit"
            ),
        )


def _save_avatar_image(path: str, content: bytes) -> None:
    """Downscale an uploaded avatar to fit within AVATAR_MAX_DIMENSION x
    AVATAR_MAX_DIMENSION (longest side, aspect ratio preserved, never
    upscaled -- Image.thumbnail() is a no-op when the source is already
    smaller) and store it as an optimized PNG, matching the .png convention
    already used for every avatar file on disk.

    Callers must run content through _reject_oversized_avatar() first.

    If the upload isn't a decodable image, we fall back to writing the raw
    bytes unchanged (the endpoint historically had no image-content
    validation, only a size cap -- this keeps that behavior rather than
    turning a previously-successful upload into a hard failure)."""
    try:
        from io import BytesIO
        from PIL import Image, ImageOps

        with Image.open(BytesIO(content)) as img:
            img.load()  # force full decode now, so truncated/bogus data raises here
            # Bake the EXIF orientation tag into the pixel data before the tag
            # is discarded by the PNG re-save below -- otherwise a portrait
            # phone-camera photo (the majority avatar source) renders sideways
            # or upside down, since PNG has no EXIF-orientation convention and
            # nothing downstream applies it.
            img = ImageOps.exif_transpose(img)
            if img.mode == "CMYK":
                img = img.convert("RGB")
            img.thumbnail((AVATAR_MAX_DIMENSION, AVATAR_MAX_DIMENSION), Image.LANCZOS)
            img.save(path, format="PNG", optimize=True)
        return
    except Exception:
        pass

    with open(path, "wb") as f:
        f.write(content)


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


class CharacterBase(BaseModel):
    """The Tavern-card fields shared by the write DTO and the read model."""

    name: str
    description: str
    nickname: Optional[str] = ""
    short_description: Optional[str] = ""
    persona_prompt: Optional[str] = ""
    scenario: Optional[str] = ""
    first_mes: Optional[str] = ""
    alternate_greetings: List[str] = []
    mes_example: Optional[str] = ""
    content_rating: Optional[str] = "limited"
    # Dynamic = persona evolves (needs decay + reflection adapts to the user);
    # static = frozen as authored (EPIC Phase 3).
    dynamic_persona: bool = True


class CharacterUpsert(CharacterBase):
    tag_ids: List[int] = []


class CharacterResponse(CharacterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    tags: List[TagSchema] = []
    state: Optional[StateResponse] = None
    avatar_url: Optional[str] = None


async def _read_upload_within_limit(file: UploadFile, kind: str) -> bytes:
    """Read an upload, rejecting anything over MAX_IMPORT_PNG_BYTES with a 413."""
    content = await file.read(MAX_IMPORT_PNG_BYTES + 1)
    if len(content) > MAX_IMPORT_PNG_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"{kind} exceeds the {MAX_IMPORT_PNG_BYTES // (1024 * 1024)}MB limit",
        )
    return content


def _parse_card_or_422(content: bytes):
    """Parse a Tavern PNG character card, surfacing any failure as a 422."""
    from src.backend.core.importer.png_parser import parse_png_character_card

    try:
        return parse_png_character_card(content)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=f"Failed to parse PNG card: {str(e)}"
        )


def _apply_upsert(char: Character, dto: CharacterUpsert, db: Session) -> None:
    """Copy card fields from an upsert DTO onto a Character and (re)associate its
    tags. Shared by create (new row) and update (existing row); an empty tag_ids
    intentionally clears the tags."""
    for key, value in dto.model_dump(exclude={"tag_ids"}).items():
        setattr(char, key, value)
    char.tags = db.query(Tag).filter(Tag.id.in_(dto.tag_ids)).all()


@router.post("/", response_model=CharacterResponse)
async def create_character(char: CharacterUpsert, db: Session = Depends(get_db)):
    new_char = Character()
    _apply_upsert(new_char, char, db)
    db.add(new_char)
    db.commit()
    db.refresh(new_char)

    # Initialize state and seed the opening greeting into a first chat so the
    # card's intro shows immediately instead of a blank chat (SEC-02).
    user = User.get_or_create_active(db)
    state = AgentState(character_id=new_char.id)
    db.add(state)
    db.flush()
    seed_initial_chat(db, new_char, user, state)
    db.commit()
    db.refresh(new_char)

    return new_char


@router.post("/import-png", response_model=CharacterResponse)
async def import_png(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await _read_upload_within_limit(file, "Character card")
    # Reject a pixel-dimension bomb before any DB row is created, not just
    # before the resize step -- so a pathological card never leaves an
    # orphaned Character row behind.
    _reject_oversized_avatar(content)
    card = _parse_card_or_422(content)

    description = card.data.description
    if card.data.personality:
        description += "\n\n" + card.data.personality
    if card.data.scenario:
        description += "\n\nScenario: " + card.data.scenario

    # Combine system_prompt if any
    if card.data.system_prompt:
        description += "\n\nSystem: " + card.data.system_prompt

    new_char = Character(
        name=card.data.name,
        description=description,
        nickname=card.data.name or "",
        short_description=card.data.description or "",
        persona_prompt=card.data.personality or "",
        scenario=card.data.scenario or "",
        first_mes=card.data.first_mes or "",
        alternate_greetings=card.data.alternate_greetings or [],
        mes_example=card.data.mes_example or "",
        content_rating="limited",
    )
    db.add(new_char)
    db.commit()
    db.refresh(new_char)

    # Save the card's embedded image as the character's avatar (downscaled).
    import os

    os.makedirs("static/avatars", exist_ok=True)
    _save_avatar_image(f"static/avatars/{new_char.id}.png", content)

    # Initialize state and seed the opening greeting into a first chat so the
    # imported card's intro shows immediately (SEC-02).
    user = User.get_or_create_active(db)
    new_state = AgentState(character_id=new_char.id)
    if card.data.first_mes:
        new_state.mood = "Neutral (start of conversation)"
    db.add(new_state)
    db.flush()
    seed_initial_chat(db, new_char, user, new_state)
    db.commit()

    # Import Lorebook (character_book)
    if card.data.character_book and "entries" in card.data.character_book:
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


@router.post("/parse-png")
async def parse_png(file: UploadFile = File(...)):
    content = await _read_upload_within_limit(file, "Character card")
    card = _parse_card_or_422(content)

    return {
        "name": card.data.name or "",
        "description": card.data.description or "",
        "personality": card.data.personality or "",
        "scenario": card.data.scenario or "",
        "first_mes": card.data.first_mes or "",
        "alternate_greetings": card.data.alternate_greetings or [],
        "mes_example": card.data.mes_example or "",
    }


@router.put("/{char_id}", response_model=CharacterResponse)
async def update_character(
    char_id: int, char: CharacterUpsert, db: Session = Depends(get_db)
):
    existing = get_or_404(db, Character, char_id, "Character")
    was_static = existing.dynamic_persona is False
    _apply_upsert(existing, char, db)
    # Re-enabling a static -> dynamic persona: re-seed the decay clock to now so
    # the frozen interval is NOT dumped as one-shot need-decay on the next turn.
    # Static freezes the simulation; without this, last_update stays stale from
    # before the static stretch and update_needs would decay energy/hunger for
    # the whole frozen period in a single tick.
    if (
        was_static
        and existing.dynamic_persona
        and existing.state
        and isinstance(existing.state.stats, dict)
    ):
        s = dict(existing.state.stats)
        s["last_update"] = datetime.now(timezone.utc).isoformat()
        existing.state.stats = s
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
async def delete_character(char_id: int, db: Session = Depends(get_db)):
    """Delete a character and ALL of its data: messages, journals, lore, chats,
    agent state, and its vector memories. Previously this orphaned every row
    (plain FKs, SQLite FK-enforcement off) so deleted characters left ghost
    messages and RAG memories that could later resurface."""
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    # Null AgentState + Chat pointers into rows we are about to delete, so the
    # explicit cleanup is FK-safe once PRAGMA foreign_keys=ON is in effect.
    state = db.query(AgentState).filter(AgentState.character_id == char_id).first()
    if state:
        state.current_message_id = None
        state.active_chat_id = None
    db.query(Chat).filter(Chat.character_id == char_id).update(
        {Chat.current_message_id: None}, synchronize_session=False
    )
    db.flush()

    db.query(MessageNode).filter(MessageNode.character_id == char_id).delete(
        synchronize_session=False
    )
    db.query(JournalEntry).filter(JournalEntry.character_id == char_id).delete(
        synchronize_session=False
    )
    db.query(LorebookEntry).filter(LorebookEntry.character_id == char_id).delete(
        synchronize_session=False
    )
    db.query(Chat).filter(Chat.character_id == char_id).delete(
        synchronize_session=False
    )
    db.delete(char)  # ORM cascade removes the 1:1 AgentState
    db.commit()

    # Purge this character's RAG memories so deleted content can never resurface.
    await vector_store.clear_character_memories(char_id)
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
            current_stats["energy"] = clamp_stat(state_data.stats.energy)
        if state_data.stats.hunger is not None:
            current_stats["hunger"] = clamp_stat(state_data.stats.hunger)
        if state_data.stats.happiness is not None:
            current_stats["happiness"] = clamp_stat(state_data.stats.happiness)
        if state_data.stats.social is not None:
            current_stats["social"] = clamp_stat(state_data.stats.social)
        if state_data.stats.is_sleeping is not None:
            current_stats["is_sleeping"] = state_data.stats.is_sleeping
        if state_data.stats.relationship_score is not None:
            rel = current_stats.get("relationship", {})
            if not isinstance(rel, dict):
                rel = {"score": DEFAULT_RELATIONSHIP_SCORE}
            rel["score"] = clamp_stat(state_data.stats.relationship_score)
            current_stats["relationship"] = rel

        # Never leave the row without a decay baseline: stats missing last_update
        # freeze need-decay forever (ST-01). Seed it if absent.
        if "last_update" not in current_stats:
            current_stats["last_update"] = datetime.now(timezone.utc).isoformat()

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


@router.post("/{char_id}/avatar")
async def upload_character_avatar(
    char_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    char = get_or_404(db, Character, char_id, "Character")
    content = await _read_upload_within_limit(file, "Avatar image")
    _reject_oversized_avatar(content)

    import os

    os.makedirs("static/avatars", exist_ok=True)
    _save_avatar_image(f"static/avatars/{char.id}.png", content)

    # No DB row is modified here (the avatar is a file on disk), so there is
    # nothing to commit.
    return {"status": "success", "avatar_url": f"/avatars/{char.id}.png"}
