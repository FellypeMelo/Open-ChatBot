import pytest
from app.db.models import AgentState, get_default_stats

def test_default_stats_contains_relationship():
    stats = get_default_stats()
    assert "relationship" in stats
    assert stats["relationship"]["score"] == 50
    assert stats["relationship"]["dynamic_preferences"] == ["teasing", "playful"]
    assert stats["relationship"]["user_sentiment"] == "Neutral"

def test_agent_state_init_with_default_relationship():
    agent = AgentState(name="Test")
    assert "relationship" in agent.stats
    assert agent.stats["relationship"]["score"] == 50
