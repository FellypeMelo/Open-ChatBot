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
    
    new_stats = engine.update_needs(initial_stats, current_time)
    
    # Energy: 100 - (2 * 5) = 90
    assert new_stats["energy"] == 90
    # Hunger: 0 + (2 * 10) = 20
    assert new_stats["hunger"] == 20
    # Social: 100 - (2 * 5) = 90
    assert new_stats["social"] == 90
    # Happiness: 100 - (2 * 2) = 96
    assert new_stats["happiness"] == 96
    # Last update should be updated
    assert new_stats["last_update"] == current_time.isoformat()

def test_agent_state_defaults():
    state = AgentState()
    assert state.stats["energy"] == 100
    assert state.stats["hunger"] == 0
    assert state.stats["happiness"] == 100
    assert state.stats["social"] == 100
    assert state.stats["is_sleeping"] is False
    assert "last_update" in state.stats
