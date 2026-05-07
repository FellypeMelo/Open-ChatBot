import pytest
from app.core.bridge import Brain
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_brain_generate_prompt():
    mock_llm = AsyncMock()
    mock_vector = AsyncMock()
    mock_vector.query_memory.return_value = {"documents": [["User likes pizza."]]}
    
    brain = Brain(llm=mock_llm, vector_store=mock_vector)
    
    # Mocking the world state
    state = {"mood": "Happy", "location": "Kitchen", "clothes": "Pajamas"}
    
    prompt = await brain.build_prompt(user_message="Hello", state=state)
    
    assert "User likes pizza." in prompt
    assert "Happy" in prompt
    assert "Kitchen" in prompt
    assert "Hello" in prompt
