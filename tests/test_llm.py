import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.core.llm import LlamaClient
from app.core.config import settings

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
    """Verify that complete() sends n_predict in the payload."""
    client = LlamaClient()
    client.client = AsyncMock()

    mock_response = MagicMock()
    mock_response.json.return_value = {"content": "Hello"}
    mock_response.raise_for_status.return_value = None
    # httpx.Response.json() is synchronous
    client.client.post.return_value = mock_response

    await client.complete("Test prompt")

    # Extract the payload sent to httpx
    call_kwargs = client.client.post.call_args
    assert call_kwargs is not None
    _args, kwargs = call_kwargs
    payload = kwargs.get("json", {})
    assert "n_predict" in payload
    assert payload["n_predict"] == settings.N_PREDICT

def test_settings_has_n_predict():
    """Config must define N_PREDICT with a reasonable value."""
    assert hasattr(settings, "N_PREDICT")
    assert settings.N_PREDICT >= 1024
