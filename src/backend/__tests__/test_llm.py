import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.backend.core.engine.llm import LlamaClient
from src.backend.core.config import settings

@pytest.mark.asyncio
async def test_llm_completion_connection_error():
    client = LlamaClient()
    client.url = "http://localhost:9999"  # Port that is likely closed
    # The error handler wraps httpx errors in HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await client.complete("Say hi")
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_llm_completion_sends_n_predict():
    """Verify that complete() configures ChatOpenAI with max_tokens (settings.N_PREDICT)."""
    from unittest.mock import patch
    
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.content = "Hello"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        
        client = LlamaClient()
        await client.complete("Test prompt")
        
        mock_chat_openai.assert_called_once()
        _, kwargs = mock_chat_openai.call_args
        assert kwargs.get("max_tokens") == settings.N_PREDICT

def test_settings_has_n_predict():
    """Config must define N_PREDICT with a reasonable value."""
    assert hasattr(settings, "N_PREDICT")
    assert settings.N_PREDICT >= 1024
