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
