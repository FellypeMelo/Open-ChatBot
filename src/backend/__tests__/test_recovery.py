import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.backend.db.models import AgentState, Character
from src.backend.core.engine.engine import evolve_character
from src.backend.api.chat import run_consciousness_layer

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
    with patch.object(db_session, 'query') as mock_query:
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
    with patch("src.backend.api.chat.SessionLocal", return_value=db_session), \
         patch("src.backend.api.chat.brain.reflect", side_effect=Exception("LLM Crash")), \
         patch("src.backend.api.chat.vector_store.add_memory") as mock_add_memory:
        
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
