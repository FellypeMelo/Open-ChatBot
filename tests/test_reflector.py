import pytest
from app.core.reflector import Reflector
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_reflector_summary():
    mock_llm = AsyncMock()
    # Mock return value to simulate LLM response
    mock_llm.complete.return_value = {"content": "The user is asking about pizza."}
    
    reflector = Reflector(llm=mock_llm)
    messages = [
        {"role": "user", "content": "I'm hungry for pizza."},
        {"role": "assistant", "content": "What kind of pizza do you like?"}
    ]
    
    summary = await reflector.reflect(messages)
    assert "pizza" in summary.lower()
