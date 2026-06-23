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


@pytest.mark.asyncio
async def test_prompt_assembly_history_and_empty_state():
    mock_vector_store = MagicMock()
    mock_vector_store.query_memory = AsyncMock(return_value={})
    mock_vector_store.query_lore = AsyncMock(return_value={})
    brain = Brain(vector_store=mock_vector_store)
    
    char = Character(name="Gemi", description="Test")
    char.id = 6

    # Test history with dict format and object format
    class MockMessage:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    history = [
        {"role": "user", "content": "Hello"},
        MockMessage("assistant", "Hi there")
    ]

    # Empty state compiles to "Status unknown."
    prompt = await brain.build_prompt("How are you?", char, state=None, history=history)
    assert "USER: Hello" in prompt
    assert "YOU: Hi there" in prompt
    assert "Status unknown." in prompt


@pytest.mark.asyncio
async def test_brain_suggest_tags():
    mock_llm = MagicMock()
    # Mock tags returned from LLM
    mock_llm.complete = AsyncMock(return_value={"content": "[1, 2, 99]"})
    
    mock_vector_store = MagicMock()
    brain = Brain(vector_store=mock_vector_store, llm_client=mock_llm)
    
    mock_tag1 = Tag(label="Tag1")
    mock_tag1.id = 1
    mock_tag2 = Tag(label="Tag2")
    mock_tag2.id = 2
    
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_tag1, mock_tag2]
    
    # Empty tags from DB case
    mock_db.query.return_value.all.return_value = []
    res_empty = await brain.suggest_tags("description", mock_db)
    assert res_empty == []

    # Valid tags case
    mock_db.query.return_value.all.return_value = [mock_tag1, mock_tag2]
    res = await brain.suggest_tags("description", mock_db)
    assert res == [1, 2] # 99 is invalid, so it is filtered out


def test_safe_json_parse():
    mock_vector_store = MagicMock()
    brain = Brain(vector_store=mock_vector_store)
    
    # 1. Standard json
    assert brain._safe_json_parse('{"a": 1}') == {"a": 1}
    
    # 2. Markdown json code block
    assert brain._safe_json_parse('```json\n{"b": 2}\n```') == {"b": 2}
    
    # 3. Generic markdown block
    assert brain._safe_json_parse('```\n{"c": 3}\n```') == {"c": 3}
    
    # 4. Parsing exception
    assert brain._safe_json_parse('invalid-json') == {}


