import pytest
from app.db.models import AgentState, get_default_stats
from app.core.social import SocialManager

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

def test_update_relationship_positive_sentiment():
    stats = {
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }
    social = SocialManager()
    updated_stats = social.update_relationship(stats, "Positive", "chat")
    
    assert updated_stats["relationship"]["score"] > 50
    assert updated_stats["relationship"]["user_sentiment"] == "Positive"

def test_update_relationship_negative_sentiment():
    stats = {
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }
    social = SocialManager()
    updated_stats = social.update_relationship(stats, "Negative", "chat")
    
    assert updated_stats["relationship"]["score"] < 50
    assert updated_stats["relationship"]["user_sentiment"] == "Negative"

def test_update_relationship_with_preference():
    stats = {
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }
    social = SocialManager()
    
    # Normal positive
    stats_normal = {
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }
    updated_normal = social.update_relationship(stats_normal, "Positive", "chat")
    gain_normal = updated_normal["relationship"]["score"] - 50
    
    # Positive with preference
    stats_pref = {
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }
    updated_pref = social.update_relationship(stats_pref, "Positive", "teasing")
    gain_pref = updated_pref["relationship"]["score"] - 50
    
    assert gain_pref > gain_normal
