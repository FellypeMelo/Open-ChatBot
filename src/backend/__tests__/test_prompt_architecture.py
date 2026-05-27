import pytest
from src.backend.core.orchestration.bridge import Brain
from src.backend.db.models import Character, User, Tag
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_prompt_assembly_with_user_and_tags():
    # Mock dependencies
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={"documents": [["Old memory"]]})
    mock_vector_store.query_lore = AsyncMock(return_value={})
    
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
    # Updated to match new template
    assert "RELATIONSHIP SCORE: 80/100" in prompt

@pytest.mark.asyncio
async def test_prompt_behavioral_modifiers_injection():
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={})
    mock_vector_store.query_lore = AsyncMock(return_value={})
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


from src.backend.core.orchestration.bridge import MASTER_PROMPT

def test_master_prompt_content():
    """Verify master prompt contains critical instructions."""
    assert "MASTER PROMPT" in MASTER_PROMPT
    assert "CORE IDENTITY" in MASTER_PROMPT
    assert "IMMERSION RULES" in MASTER_PROMPT
    assert "*asterisks*" in MASTER_PROMPT
    assert "quotes" in MASTER_PROMPT

@pytest.mark.asyncio
async def test_lorebook_injection_in_prompt():
    """Verify that matching lorebook entries are injected into the prompt."""
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={})
    mock_vector_store.query_lore = AsyncMock(return_value={
        "documents": [["Sword of Destiny lore content"]]
    })
    brain = Brain(vector_store=mock_vector_store)

    char = Character(name="Gemi", description="Test")
    char.id = 5
    state = {"stats": {"energy": 100, "hunger": 0, "relationship": {"score": 50}}}

    prompt = await brain.build_prompt("I draw my sword", char, state)

    assert "RELEVANT WORLD LORE:" in prompt
    assert "Sword of Destiny lore content" in prompt
