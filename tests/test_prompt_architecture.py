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


from app.core.bridge import MASTER_PROMPT

ORIGINAL_PROMPT_LENGTH = 4971  # length of the original MASTER_PROMPT constant

def test_master_prompt_condensed():
    """Condensed prompt should be significantly shorter than original."""
    assert len(MASTER_PROMPT) < ORIGINAL_PROMPT_LENGTH
    # Should be at most ~60% of original length
    assert len(MASTER_PROMPT) < int(ORIGINAL_PROMPT_LENGTH * 0.6)

def test_critical_sections_preserved():
    """All critical sections must remain in the condensed prompt."""
    assert "OUTPUT FORMAT" in MASTER_PROMPT or "RESPONSE FORMAT" in MASTER_PROMPT
    assert "*asterisks*" in MASTER_PROMPT
    assert "narrative" in MASTER_PROMPT or "prose" in MASTER_PROMPT
    assert "dialogue" in MASTER_PROMPT or "quotes" in MASTER_PROMPT
    assert "CRITICAL RULES" in MASTER_PROMPT or "CRITICAL IMMERSION RULES" in MASTER_PROMPT
    assert "in-character" in MASTER_PROMPT or "stay in-character" in MASTER_PROMPT

def test_immersion_rules_preserved():
    """Key behavior rules must survive condensation."""
    assert "fictional" in MASTER_PROMPT or "AI" in MASTER_PROMPT
    assert "Never mention" in MASTER_PROMPT or "NEVER" in MASTER_PROMPT


@pytest.mark.asyncio
async def test_few_shot_examples_in_prompt():
    """Assembled prompt must contain concrete few-shot examples."""
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={"documents": [[]]})
    brain = Brain(vector_store=mock_vector_store)

    char = Character(name="Gemi", description="Test character")
    char.id = 3
    state = {"stats": {"energy": 100, "hunger": 0, "relationship": {"score": 50}}}

    prompt = await brain.build_prompt("Hello!", char, state)

    # Must contain a concrete example with an Input/Output pair
    assert "Input:" in prompt
    assert "Output:" in prompt

@pytest.mark.asyncio
async def test_few_shot_examples_position():
    """Few-shot examples must be placed between USER MESSAGE and RESPONSE."""
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={"documents": [[]]})
    brain = Brain(vector_store=mock_vector_store)

    char = Character(name="Gemi", description="Test character")
    char.id = 4
    state = {"stats": {"energy": 100, "hunger": 0, "relationship": {"score": 50}}}

    prompt = await brain.build_prompt("Hello!", char, state)

    user_msg_pos = prompt.find("USER MESSAGE:")
    examples_pos = prompt.find("EXAMPLES OF GOOD RESPONSES")
    response_pos = prompt.find("### RESPONSE ###")

    assert user_msg_pos >= 0, "USER MESSAGE: must exist"
    assert response_pos >= 0, "### RESPONSE ### must exist"
    assert examples_pos >= 0, "EXAMPLES OF GOOD RESPONSES must exist"
    assert user_msg_pos < examples_pos < response_pos, \
        "EXAMPLES must be between USER MESSAGE and ### RESPONSE ###"
