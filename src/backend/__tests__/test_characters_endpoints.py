"""
Coverage-focused tests for src/backend/api/characters.py.

Existing character CRUD happy-path coverage already lives in
test_character_systems.py (create/read/list/update/delete) and test_api.py
(update_character_state with an existing AgentState). This file fills the
remaining gaps: tag-id assignment on create, the update-404 case, the whole
import-png flow (happy path, oversized upload, unparseable upload, character
book -> lorebook import), avatar_url population on list/get, the delete-404
case, state updates that must create a brand-new AgentState plus clamp/
fallback branches, and the journal endpoint ordering.
"""

from unittest.mock import patch

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.backend.api.characters import MAX_IMPORT_PNG_BYTES
from src.backend.core.importer.png_parser import TavernV2Card, TavernV2Data
from src.backend.db.models import (
    AgentState,
    Character,
    JournalEntry,
    LorebookEntry,
    Tag,
)


def _stub_card(**data_overrides):
    data = TavernV2Data(
        name="Aria",
        description="A stub character.",
        **data_overrides,
    )
    return TavernV2Card(data=data)


def test_create_character_with_tag_ids(client, db_session):
    tag = Tag(label="Adventurous", instruction="Be bold.")
    db_session.add(tag)
    db_session.commit()

    response = client.post(
        "/characters/",
        json={
            "name": "Rook",
            "description": "A stalwart guardian.",
            "tag_ids": [tag.id],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rook"
    assert len(data["tags"]) == 1
    assert data["tags"][0]["label"] == "Adventurous"
    assert data["state"] is not None


def test_update_character_success(client, db_session):
    char = Character(name="Original", description="Before")
    db_session.add(char)
    db_session.commit()

    tag = Tag(label="Calm", instruction="Speak softly.")
    db_session.add(tag)
    db_session.commit()

    response = client.put(
        f"/characters/{char.id}",
        json={"name": "Renamed", "description": "After", "tag_ids": [tag.id]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Renamed"
    assert data["description"] == "After"
    assert len(data["tags"]) == 1
    assert data["tags"][0]["label"] == "Calm"


def test_update_character_not_found(client, db_session):
    response = client.put(
        "/characters/999999",
        json={"name": "Nobody", "description": "Doesn't exist"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_get_character_not_found(client, db_session):
    response = client.get("/characters/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_delete_character_not_found(client, db_session):
    response = client.delete("/characters/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_list_characters_populates_avatar_url_when_file_exists(client, db_session):
    char = Character(name="Painted", description="Has an avatar on disk")
    db_session.add(char)
    db_session.commit()

    with patch("os.path.exists", return_value=True):
        response = client.get("/characters/")

    assert response.status_code == 200
    matching = [c for c in response.json() if c["id"] == char.id]
    assert len(matching) == 1
    assert matching[0]["avatar_url"] == f"/avatars/{char.id}.png"


def test_get_character_populates_avatar_url_when_file_exists(client, db_session):
    char = Character(name="Painted", description="Has an avatar on disk")
    db_session.add(char)
    db_session.commit()

    with patch("os.path.exists", return_value=True):
        response = client.get(f"/characters/{char.id}")

    assert response.status_code == 200
    assert response.json()["avatar_url"] == f"/avatars/{char.id}.png"


def test_import_png_happy_path(client, db_session, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    card = _stub_card(
        personality="Kind and curious",
        scenario="A quiet library",
        system_prompt="Stay in character",
        first_mes="Hello there!",
    )

    with patch(
        "src.backend.core.importer.png_parser.parse_png_character_card",
        return_value=card,
    ):
        response = client.post(
            "/characters/import-png",
            files={"file": ("card.png", b"\x89PNG\r\n\x1a\nfake-payload", "image/png")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aria"
    assert "A stub character." in data["description"]
    assert "Kind and curious" in data["description"]
    assert "Scenario: A quiet library" in data["description"]
    assert "System: Stay in character" in data["description"]
    assert data["avatar_url"] == f"/avatars/{data['id']}.png"

    saved_avatar = tmp_path / "static" / "avatars" / f"{data['id']}.png"
    assert saved_avatar.exists()

    state = (
        db_session.query(AgentState)
        .filter(AgentState.character_id == data["id"])
        .first()
    )
    assert state is not None
    assert state.mood == "Neutral (start of conversation)"


def test_import_png_unparseable_returns_422(client, db_session):
    with patch(
        "src.backend.core.importer.png_parser.parse_png_character_card",
        side_effect=ValueError("Character metadata not found in image"),
    ):
        response = client.post(
            "/characters/import-png",
            files={"file": ("bad.png", b"not-a-real-png", "image/png")},
        )

    assert response.status_code == 422
    assert "Failed to parse PNG card" in response.json()["detail"]


def test_import_png_over_size_limit_returns_413(client, db_session):
    oversized_content = b"0" * (MAX_IMPORT_PNG_BYTES + 1)

    response = client.post(
        "/characters/import-png",
        files={"file": ("huge.png", oversized_content, "image/png")},
    )

    assert response.status_code == 413
    assert "exceeds the" in response.json()["detail"]


def test_import_png_with_character_book_creates_lorebook_entries(
    client, db_session, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)

    card = _stub_card(
        character_book={
            "entries": [
                {"keys": ["sword", "blade"], "content": "A legendary weapon."},
                {"keys": [], "content": "An entry with no keys."},
            ]
        }
    )

    with patch(
        "src.backend.core.importer.png_parser.parse_png_character_card",
        return_value=card,
    ):
        response = client.post(
            "/characters/import-png",
            files={"file": ("card.png", b"\x89PNG\r\n\x1a\nfake-payload", "image/png")},
        )

    assert response.status_code == 200
    char_id = response.json()["id"]

    entries = (
        db_session.query(LorebookEntry)
        .filter(LorebookEntry.character_id == char_id)
        .order_by(LorebookEntry.id)
        .all()
    )
    assert len(entries) == 2
    assert entries[0].keyword == "sword,blade"
    assert entries[0].content == "A legendary weapon."
    assert entries[0].is_global is False
    assert entries[1].keyword == ""
    assert entries[1].content == "An entry with no keys."


def test_update_character_state_not_found(client, db_session):
    response = client.put(
        "/characters/999999/state",
        json={"location": "Nowhere"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_update_character_state_creates_new_state_when_missing(client, db_session):
    char = Character(name="Stateless", description="No AgentState yet")
    db_session.add(char)
    db_session.commit()

    response = client.put(
        f"/characters/{char.id}/state",
        json={
            "location": "Garden",
            "mood": "Curious",
            "clothes": "Sundress",
            "stats": {"energy": 42},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["state"]["location"] == "Garden"
    assert data["state"]["mood"] == "Curious"
    assert data["state"]["clothes"] == "Sundress"
    assert data["state"]["stats"]["energy"] == 42

    created_state = (
        db_session.query(AgentState).filter(AgentState.character_id == char.id).first()
    )
    assert created_state is not None


def test_update_character_state_clamps_stats_and_fixes_bad_relationship(
    client, db_session
):
    char = Character(name="Clamped", description="Has out-of-range stats incoming")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=char.id)
    # Corrupt the relationship field so the handler must fall back to a fresh dict.
    state.stats = {**state.stats, "relationship": "not-a-dict"}
    db_session.add(state)
    db_session.commit()

    response = client.put(
        f"/characters/{char.id}/state",
        json={
            "stats": {
                "happiness": 500,
                "social": -50,
                "is_sleeping": True,
                "relationship_score": 999,
            }
        },
    )

    assert response.status_code == 200
    stats = response.json()["state"]["stats"]
    assert stats["happiness"] == 100
    assert stats["social"] == 0
    assert stats["is_sleeping"] is True
    assert stats["relationship"]["score"] == 100


def test_update_character_state_retries_once_on_conflict():
    # Regression test: AgentState carries an optimistic-concurrency version
    # column, so a same-user race (e.g. a stat button clicked while a chat
    # turn's decay commit is in flight -- found via e2e testing) can raise
    # StaleDataError on commit. This is routine contention, not a real
    # multi-writer conflict, so the endpoint retries once against fresh data
    # instead of failing a low-stakes stat tweak outright.
    #
    # Uses a dedicated engine + a fresh session per request (mirroring
    # production's per-request SessionLocal()) instead of the shared
    # client/db_session fixture: that fixture wraps the whole test in one
    # external transaction, so the endpoint's own db.rollback() on the
    # simulated conflict would wipe this test's own fixture data too, which
    # can never happen in production where every request gets an independent
    # session/transaction.
    import os
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient
    from src.backend.db.database import Base, get_db
    from src.backend.main import app

    # A real temp file (not sqlite:///:memory:) so every session/connection
    # from this engine sees the same data -- an in-memory DB is scoped to a
    # single connection, which would make the TestClient's request-scoped
    # session unable to see this test's own setup rows.
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        setup_db = TestSessionLocal()
        char = Character(name="Racer", description="Concurrent update target")
        setup_db.add(char)
        setup_db.commit()
        state = AgentState(character_id=char.id)
        setup_db.add(state)
        setup_db.commit()
        char_id = char.id
        setup_db.close()

        real_commit = Session.commit
        call_count = {"n": 0}

        def flaky_commit(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise StaleDataError("stale")
            return real_commit(self, *args, **kwargs)

        with patch("sqlalchemy.orm.Session.commit", flaky_commit):
            with TestClient(app) as client:
                response = client.put(
                    f"/characters/{char_id}/state", json={"location": "Kitchen"}
                )

        assert response.status_code == 200
        assert response.json()["state"]["location"] == "Kitchen"
        assert call_count["n"] == 2

        verify_db = TestSessionLocal()
        refreshed = verify_db.query(Character).filter_by(id=char_id).first()
        assert refreshed.state.location == "Kitchen"
        verify_db.close()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        os.close(db_fd)
        try:
            os.unlink(db_path)
        except OSError:
            pass


def test_journal_entries_returned_newest_first(client, db_session):
    char = Character(name="Journaled", description="Has journal entries")
    db_session.add(char)
    db_session.commit()

    from datetime import datetime, timedelta, timezone

    base = datetime.now(timezone.utc)
    oldest = JournalEntry(
        character_id=char.id,
        timestamp=base - timedelta(days=2),
        content="Oldest entry",
        summary="old",
        mood_at_time="Calm",
        relationship_score=50,
        energy_level=80,
    )
    newest = JournalEntry(
        character_id=char.id,
        timestamp=base,
        content="Newest entry",
        summary="new",
        mood_at_time="Excited",
        relationship_score=60,
        energy_level=90,
    )
    middle = JournalEntry(
        character_id=char.id,
        timestamp=base - timedelta(days=1),
        content="Middle entry",
        summary="mid",
        mood_at_time="Neutral",
        relationship_score=55,
        energy_level=85,
    )
    db_session.add_all([oldest, newest, middle])
    db_session.commit()

    response = client.get(f"/characters/{char.id}/journal")

    assert response.status_code == 200
    data = response.json()
    assert [entry["content"] for entry in data] == [
        "Newest entry",
        "Middle entry",
        "Oldest entry",
    ]
    assert data[0]["mood_at_time"] == "Excited"
    assert data[0]["relationship_score"] == 60
    assert data[0]["energy_level"] == 90
