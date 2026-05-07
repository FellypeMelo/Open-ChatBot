import pytest
import json
from app.core.reflector import Reflector
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_reflector_summary():
    mock_llm = AsyncMock()
    # Mock return value to simulate structured JSON response
    response_data = {
        "summary": "The user is asking about pizza.",
        "facts": ["User likes pizza"],
        "traits": ["hungry"]
    }
    mock_llm.complete.return_value = {"content": json.dumps(response_data)}
    
    reflector = Reflector(llm=mock_llm)
    messages = [
        {"role": "user", "content": "I'm hungry for pizza."},
        {"role": "assistant", "content": "What kind of pizza do you like?"}
    ]
    
    result = await reflector.reflect(messages)
    assert isinstance(result, dict)
    assert "summary" in result
    assert "pizza" in result["summary"].lower()
    assert result["facts"] == ["User likes pizza"]
    assert result["traits"] == ["hungry"]

@pytest.mark.asyncio
async def test_reflector_llm_failure():
    mock_llm = AsyncMock()
    # Simulate LLM call failure
    mock_llm.complete.side_effect = Exception("LLM connection error")
    
    reflector = Reflector(llm=mock_llm)
    messages = [{"role": "user", "content": "Hello"}]
    
    result = await reflector.reflect(messages)
    assert isinstance(result, dict)
    assert result["summary"] == "Error during reflection."
    assert result["facts"] == []
    assert result["traits"] == []

@pytest.mark.asyncio
async def test_reflector_json_parse_failure():
    mock_llm = AsyncMock()
    # Simulate invalid JSON response
    mock_llm.complete.return_value = {"content": "Not a JSON object"}
    
    reflector = Reflector(llm=mock_llm)
    messages = [{"role": "user", "content": "Hello"}]
    
    result = await reflector.reflect(messages)
    assert isinstance(result, dict)
    assert result["summary"] == "Not a JSON object"
    assert result["facts"] == []
    assert result["traits"] == []

@pytest.mark.asyncio
async def test_reflector_message_limit():
    mock_llm = AsyncMock()
    mock_llm.complete.return_value = {"content": "{}"}
    
    reflector = Reflector(llm=mock_llm)
    # 15 messages
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]
    
    await reflector.reflect(messages)
    
    # Verify that only the last 10 messages were used in the prompt
    # The prompt starts with the instructions and then appends messages
    called_prompt = mock_llm.complete.call_args[0][0]
    assert "Message 0" not in called_prompt
    assert "Message 4" not in called_prompt
    assert "Message 5" in called_prompt
    assert "Message 14" in called_prompt
