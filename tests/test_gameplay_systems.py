import pytest
from app.db.models import Character, AgentState
from app.core.world import WorldEngine
from datetime import datetime, timedelta

def test_stat_drain_over_time():
    world = WorldEngine()
    
    now = datetime.now()
    two_hours_ago = now - timedelta(hours=2)
    
    # 100% stats
    initial_stats = {
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": two_hours_ago.isoformat()
    }
    
    # 2 hours passed
    updated = world.update_needs(initial_stats, now)
    
    # Energy drain rate is 5.0 per hour -> 100 - 10 = 90
    assert updated["energy"] == 90
    # Hunger increase rate is 10.0 per hour -> 0 + 20 = 20
    assert updated["hunger"] == 20
    # Happiness decrease rate is 2.0 per hour -> 100 - 4 = 96
    assert updated["happiness"] == 96

def test_energy_recovery_during_sleep():
    world = WorldEngine()
    
    now = datetime.now()
    four_hours_ago = now - timedelta(hours=4)
    
    # Low energy, sleeping
    initial_stats = {
        "energy": 20,
        "is_sleeping": True,
        "last_update": four_hours_ago.isoformat()
    }
    
    # 4 hours passed
    # Recovery rate is 10.0 per hour -> 20 + 40 = 60
    updated = world.update_energy(initial_stats, now)
    assert updated["energy"] == 60

def test_state_synchronization_in_api(client, db_session):
    # Setup character with old update time
    char = Character(id=1, name="Luna", description="Test")
    db_session.add(char)
    
    fixed_now = datetime(2026, 5, 8, 12, 0, 0)
    old_time = (fixed_now - timedelta(hours=10)).isoformat()
    state = AgentState(character_id=1, stats={
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": old_time
    })
    db_session.add(state)
    db_session.commit()

    from unittest.mock import patch, AsyncMock
    with patch("app.core.bridge.VectorStore.query_memory", new_callable=AsyncMock) as mock_query, \
         patch("app.api.chat.LlamaClient.complete") as mock_complete, \
         patch("app.api.chat.datetime") as mock_datetime:
        
        mock_datetime.now.return_value = fixed_now
        mock_query.return_value = {}
        mock_complete.return_value = {"content": "*Nods.* \"Hello.\""}
        
        response = client.post("/chat", json={"message": "hello", "character_id": 1})
        assert response.status_code == 200
        data = response.json()
        
        # Energy should be 100 - (10 * 5) = 50
        assert data["stats"]["energy"] == 50
        # Hunger should be 0 + (10 * 10) = 100
        assert data["stats"]["hunger"] == 100
