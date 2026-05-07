import pytest
from app.core.bridge import Brain
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_brain_generate_prompt():
    mock_vector = AsyncMock()
    mock_vector.query_memory.return_value = {"documents": [["User likes pizza."]]}
    
    brain = Brain(vector_store=mock_vector)
    
    # Mocking the world state
    state = {"mood": "Happy", "location": "Kitchen", "clothes": "Pajamas"}
    
    prompt = await brain.build_prompt(user_message="Hello", state=state)
    
    assert "User likes pizza." in prompt
    assert "Happy" in prompt
    assert "Kitchen" in prompt
    assert "Hello" in prompt
    assert "### INSTRUCTIONS ###" in prompt

@pytest.mark.asyncio
async def test_brain_empty_memory():
    mock_vector = AsyncMock()
    # Empty documents list
    mock_vector.query_memory.return_value = {"documents": [[]]}
    
    brain = Brain(vector_store=mock_vector)
    prompt = await brain.build_prompt(user_message="Hello", state={})
    
    assert "No relevant memory found." in prompt

@pytest.mark.asyncio
async def test_brain_empty_state():
    mock_vector = AsyncMock()
    mock_vector.query_memory.return_value = {"documents": [["Memory"]]}
    
    brain = Brain(vector_store=mock_vector)
    prompt = await brain.build_prompt(user_message="Hello", state={})
    
    assert "No active state variables." in prompt

@pytest.mark.asyncio
async def test_brain_complex_state():
    mock_vector = AsyncMock()
    mock_vector.query_memory.return_value = {"documents": [["Likes teasing."]]}
    
    brain = Brain(vector_store=mock_vector)
    
    state = {
        "name": "Gemi",
        "location": "Living Room",
        "mood": "Happy",
        "stats": {
            "energy": 80,
            "hunger": 20,
            "happiness": 90,
            "social": 70,
            "is_sleeping": False,
            "relationship": {
                "score": 75,
                "user_sentiment": "Friendly",
                "dynamic_preferences": ["teasing", "jokes"]
            }
        }
    }
    
    prompt = await brain.build_prompt(user_message="Tell me a joke", state=state)
    
    assert "BIOLOGICAL NEEDS:" in prompt
    assert "Energy: 80/100" in prompt
    assert "Hunger: 20/100" in prompt
    assert "RELATIONSHIP STATUS:" in prompt
    assert "Score: 75/100" in prompt
    assert "User Sentiment: Friendly" in prompt
    assert "teasing, jokes" in prompt
    assert "PERSONALITY QUIRKS:" in prompt
    assert "teasing and playful banter" in prompt
