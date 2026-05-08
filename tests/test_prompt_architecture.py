import pytest
from app.core.bridge import Brain
from app.db.models import Character, User, Tag
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_prompt_assembly_with_user_and_tags():
    # Mock dependencies
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={"documents": [["Old memory"]]})
    
    brain = Brain(vector_store=mock_vector_store)
    
    # Setup Data
    char = Character(name="Gemi", description="Feisty entity")
    char.id = 1
    tag = Tag(label="Playful", instruction="Be teasing.")
    char.tags = [tag]
    
    user = User(name="Alice", gender="Female")
    
    state = {
        "location": "Living Room",
        "mood": "Happy",
        "stats": {
            "energy": 100,
            "hunger": 0,
            "happiness": 100,
            "social": 100,
            "relationship": {"score": 80, "user_sentiment": "Friendly"}
        }
    }
    
    prompt = await brain.build_prompt("Hello!", char, state, user=user)
    
    # Assertions
    assert "NAME: Gemi" in prompt
    assert "Alice" in prompt
    assert "Female" in prompt
    assert "PLAYFUL: Be teasing." in prompt
    assert "Old memory" in prompt
    assert "Score: 80/100" in prompt

@pytest.mark.asyncio
async def test_prompt_behavioral_modifiers_injection():
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={})
    brain = Brain(vector_store=mock_vector_store)
    
    char = Character(name="Luna", description="Calm")
    char.id = 2
    char.tags = []
    
    # Critical stats: Exhausted and Starving
    state = {
        "stats": {
            "energy": 10,
            "hunger": 90,
            "relationship": {"score": 50}
        }
    }
    
    prompt = await brain.build_prompt("Hi", char, state)
    
    assert "EXHAUSTED" in prompt
    assert "STARVING" in prompt
