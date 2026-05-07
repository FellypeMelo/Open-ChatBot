import pytest
from datetime import datetime, timedelta
from app.core.world import WorldEngine
from app.db.models import AgentState

def test_needs_drain():
    engine = WorldEngine()
    initial_stats = {
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": "2026-05-07T10:00:00"
    }
    
    # 2 hours later
    current_time = datetime.fromisoformat("2026-05-07T12:00:00")
    
    # This should fail as update_needs is not implemented
    new_stats = engine.update_needs(initial_stats, current_time)
    
    # Expect hunger to increase
    assert new_stats["hunger"] > 0
    # Expect social to decrease
    assert new_stats["social"] < 100
    # Expect happiness to decrease
    assert new_stats["happiness"] < 100

def test_agent_state_defaults():
    # This should fail if models.py is not updated yet
    state = AgentState()
    assert "hunger" in state.stats
    assert state.stats["hunger"] == 0
    assert state.stats["happiness"] == 100
    assert state.stats["social"] == 100
