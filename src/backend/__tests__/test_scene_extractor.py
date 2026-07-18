"""EPIC Phase 2: per-turn scene extractor + mirror-aware apply.

Isolated: the LLM is mocked (no llama-server); apply runs against the isolated
temp SQLite from conftest.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.backend.core.orchestration.bridge import Brain
from src.backend.core.engine.engine import apply_scene_update
from src.backend.db.models import Character, AgentState, Chat


def test_scene_gate_runs_only_on_movement():
    from src.backend.api.chat import _reply_suggests_scene_change

    # movement / transition language -> worth an extraction
    assert _reply_suggests_scene_change("She walks into the kitchen.")
    assert _reply_suggests_scene_change("He heads down the corridor toward the exit.")
    assert _reply_suggests_scene_change("The elevator doors open and she steps out.")
    assert _reply_suggests_scene_change("She leaves the office, making her way home.")
    # pure dialogue / emotion -> skip the LLM call (location can't have changed)
    assert not _reply_suggests_scene_change(
        '"You look tired," she says, smiling softly.'
    )
    assert not _reply_suggests_scene_change(
        "Elara rubs her temple and lets out a dry laugh."
    )
    assert not _reply_suggests_scene_change("")


def _brain_with_llm(content):
    llm = MagicMock()
    llm.url = "http://127.0.0.1:8080"
    llm.complete = AsyncMock(return_value={"content": content})
    return Brain(MagicMock(), llm_client=llm)


def test_extract_scene_parses_location_and_mood():
    brain = _brain_with_llm('{"location": "Elevator", "mood": "Anxious"}')
    scene = asyncio.run(
        brain.extract_scene("She steps into the elevator.", "Office", "Tired")
    )
    assert scene["location"] == "Elevator"
    assert scene["mood"] == "Anxious"


def test_extract_scene_empty_reply_skips_llm():
    llm = MagicMock()
    llm.url = "http://127.0.0.1:8080"
    llm.complete = AsyncMock()
    brain = Brain(MagicMock(), llm_client=llm)
    assert asyncio.run(brain.extract_scene("   ")) == {}
    llm.complete.assert_not_called()


def test_apply_scene_update_updates_live_agent(db_session):
    char = Character(id=600, name="SceneChar", description="d")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=600, location="Office", mood="Tired")
    state.active_chat_id = 42
    db_session.add(state)
    db_session.commit()

    apply_scene_update(
        db_session, 600, {"location": "elevator", "mood": "Anxious"}, active_chat_id=42
    )

    db_session.refresh(state)
    assert state.location == "Elevator"  # normalize_state_label capitalizes
    assert state.mood == "Anxious"


def test_apply_scene_update_targets_background_chat_when_switched(db_session):
    # Agent mirrors a different (active) chat; the scene belongs to background
    # chat `bg` -> apply to bg's snapshot, never the live agent (no bleed).
    char = Character(id=601, name="SceneChar2", description="d")
    db_session.add(char)
    db_session.commit()
    bg = Chat(character_id=601, title="bg", location="Cafe", mood="Calm")
    db_session.add(bg)
    db_session.commit()
    state = AgentState(character_id=601, location="Office", mood="Tired")
    state.active_chat_id = 999  # a DIFFERENT active chat
    db_session.add(state)
    db_session.commit()

    apply_scene_update(
        db_session, 601, {"location": "Rooftop", "mood": "Tense"}, active_chat_id=bg.id
    )

    db_session.refresh(state)
    db_session.refresh(bg)
    assert bg.location == "Rooftop"  # background chat updated
    assert state.location == "Office"  # live agent untouched


def test_apply_scene_update_ignores_empty_scene(db_session):
    char = Character(id=602, name="SceneChar3", description="d")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=602, location="Office", mood="Tired")
    db_session.add(state)
    db_session.commit()

    apply_scene_update(db_session, 602, {}, active_chat_id=None)

    db_session.refresh(state)
    assert state.location == "Office"  # unchanged
