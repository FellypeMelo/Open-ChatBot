import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError
from src.backend.db.database import Base
from src.backend.db.models import AgentState, Character
from src.backend.core.engine.engine import evolve_character
from src.backend.api.chat import run_consciousness_layer


def test_evolve_character_retries_on_stale_data_error():
    # RF-02: a concurrent chat commit advances AgentState.version; evolve's
    # commit then raises StaleDataError. It must re-query fresh state and retry,
    # not swallow the whole reflection (relationship/summary/facts/journal lost).
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    try:
        char = Character(name="Retry", description="d")
        db.add(char)
        db.commit()
        db.add(AgentState(character_id=char.id))
        db.commit()

        real_commit = db.commit
        calls = {"n": 0}

        def flaky_commit():
            calls["n"] += 1
            if calls["n"] == 1:
                raise StaleDataError("simulated concurrent update")
            return real_commit()

        with patch.object(db, "commit", side_effect=flaky_commit):
            evolve_character(db, char.id, {"relationship_change": 5})

        state = db.query(AgentState).filter_by(character_id=char.id).first()
        db.refresh(state)
        # Applied exactly once on the retry (55, not 50 swallowed nor 60 double).
        assert state.stats["relationship"]["score"] == 55
        assert calls["n"] == 2
    finally:
        db.close()
        engine.dispose()


def test_evolve_character_race_condition_safety(db_session):
    """Verifies that with_for_update is called to prevent race conditions."""
    # Setup
    char = Character(name="Test", description="Test desc")
    db_session.add(char)
    db_session.commit()

    state = AgentState(character_id=char.id)
    db_session.add(state)
    db_session.commit()

    # We mock the query to verify with_for_update was chained
    with patch.object(db_session, "query") as mock_query:
        mock_filter = mock_query.return_value.filter.return_value
        mock_lock = mock_filter.with_for_update.return_value
        mock_lock.first.return_value = state

        evolve_character(db_session, char.id, {"summary": "New summary"})

        # Verify call chain
        assert mock_filter.with_for_update.called
        assert mock_lock.first.called


@pytest.mark.asyncio
async def test_reflection_failure_resilience(db_session):
    """Verifies that a crash in brain.reflect doesn't corrupt the DB session or block storage."""
    char = Character(name="Test", description="Test desc")
    db_session.add(char)
    db_session.commit()

    # We need to mock SessionLocal to return our test db_session
    with (
        patch("src.backend.api.chat.SessionLocal", return_value=db_session),
        patch("src.backend.api.chat.brain.reflect", side_effect=Exception("LLM Crash")),
        patch("src.backend.api.chat.vector_store.add_memory") as mock_add_memory,
    ):
        # This should log an exception but not raise one (background task)
        await run_consciousness_layer(char.id, "Hello", "Hi", force_reflect=True)

        # Memory storage should still have been attempted before the crash
        assert mock_add_memory.called
        # Verify the session is still usable (no uncommitted state)
        assert db_session.query(Character).count() == 1


def test_state_initialization_defaults():
    """Ensures AgentState defaults are robust and prevent null pointer errors in FE."""
    state = AgentState(character_id=1)
    assert state.location == "Living Room"
    assert state.clothes == "Casual"
    assert state.mood == "Neutral"
    assert state.stats["energy"] == 100
    assert state.stats["relationship"]["score"] == 50


def test_evolve_character_relationship_change(db_session):
    """Verifies that evolve_character updates the relationship score correctly."""
    char = Character(name="Test", description="Test desc")
    db_session.add(char)
    db_session.commit()

    state = AgentState(character_id=char.id)
    db_session.add(state)
    db_session.commit()

    # Evolve with a positive relationship change
    evolve_character(db_session, char.id, {"relationship_change": 5})

    db_session.refresh(state)
    assert state.stats["relationship"]["score"] == 55

    # Evolve with a negative relationship change
    evolve_character(db_session, char.id, {"relationship_change": -10})
    db_session.refresh(state)
    assert state.stats["relationship"]["score"] == 45


def test_evolve_character_tag_evolution(db_session):
    """Verifies that evolve_character swaps character tags dynamically based on relationship score thresholds."""
    from src.backend.db.models import Tag

    # Create tags in db
    distant_tag = Tag(label="emotionally distant", instruction="Be distant.")
    guarded_tag = Tag(label="guarded", instruction="Be guarded.")
    db_session.add_all([distant_tag, guarded_tag])
    db_session.commit()

    char = Character(
        name="Luna", description="Luna character", tags=[distant_tag, guarded_tag]
    )
    db_session.add(char)
    db_session.commit()

    state = AgentState(character_id=char.id)
    # Start at relationship score 50
    state.stats["relationship"]["score"] = 50
    db_session.add(state)
    db_session.commit()

    # Verify initial tags
    assert len(char.tags) == 2
    assert "emotionally distant" in [t.label.lower() for t in char.tags]
    assert "guarded" in [t.label.lower() for t in char.tags]

    # Warm to 85: evolution LAYERS affectionate + vulnerable on top; the
    # author-defined distant + guarded are preserved (RF-06 option C).
    evolve_character(db_session, char.id, {"relationship_change": 35})
    db_session.refresh(char)

    tag_labels = [t.label.lower() for t in char.tags]
    assert "affectionate" in tag_labels
    assert "vulnerable" in tag_labels
    assert "emotionally distant" in tag_labels  # authored, retained
    assert "guarded" in tag_labels  # authored, retained

    # Cool to 25: evolution removes ONLY the warmth it added; authored tags stay.
    evolve_character(db_session, char.id, {"relationship_change": -60})
    db_session.refresh(char)

    tag_labels_low = [t.label.lower() for t in char.tags]
    assert "affectionate" not in tag_labels_low
    assert "vulnerable" not in tag_labels_low
    assert "emotionally distant" in tag_labels_low  # authored, retained
    assert "guarded" in tag_labels_low


def test_evolve_character_preserves_authored_warm_tag_on_cold_swing(db_session):
    # RF-06 (option C): a tag the AUTHOR defined must never be deleted by tag
    # evolution -- only evolution-owned tags are removable.
    from src.backend.db.models import Tag

    authored = Tag(label="affectionate", instruction="Authored: always warm.")
    db_session.add(authored)
    db_session.commit()

    char = Character(name="Sunny", description="Warm by design", tags=[authored])
    db_session.add(char)
    db_session.commit()

    state = AgentState(character_id=char.id)
    state.stats["relationship"]["score"] = 50
    db_session.add(state)
    db_session.commit()

    # Relationship collapses well below the cold threshold.
    evolve_character(db_session, char.id, {"relationship_change": -40})  # 50 -> 10
    db_session.refresh(char)

    labels = [t.label.lower() for t in char.tags]
    assert "affectionate" in labels, "authored tag must survive a cold swing"
