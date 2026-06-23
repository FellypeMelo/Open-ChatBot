import pytest
import sys
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
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
    await client.close()

@pytest.mark.asyncio
async def test_llm_completion_sends_n_predict():
    """Verify that complete() configures ChatOpenAI with max_tokens (settings.N_PREDICT)."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.content = "Hello"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        
        client = LlamaClient()
        result = await client.complete("Test prompt")
        assert result == {"content": "Hello"}
        
        mock_chat_openai.assert_called_once()
        _, kwargs = mock_chat_openai.call_args
        assert kwargs.get("max_tokens") == settings.N_PREDICT
        await client.close()

def test_settings_has_n_predict():
    """Config must define N_PREDICT with a reasonable value."""
    assert hasattr(settings, "N_PREDICT")
    assert settings.N_PREDICT >= 1024

def test_llama_client_url_getters_setters():
    client = LlamaClient()
    client.url = "http://custom-inference:8080"
    client.embedding_url = "http://custom-embedding:8081"
    assert client.url == "http://custom-inference:8080"
    assert client.embedding_url == "http://custom-embedding:8081"

@pytest.mark.asyncio
async def test_llm_completion_stream():
    """Verify that complete_stream() streams tokens from astream."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        # Define mock async generator chunks
        async def mock_astream(*args, **kwargs):
            yield MagicMock(content="Hello ")
            yield MagicMock(content="world!")
            
        mock_instance.astream = mock_astream
        
        client = LlamaClient()
        tokens = []
        async for token in client.complete_stream("Test stream prompt"):
            tokens.append(token)
            
        assert tokens == ["Hello ", "world!"]
        await client.close()

@pytest.mark.asyncio
async def test_llm_completion_stream_error():
    """Verify stream handles exceptions by raising HTTPException."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        async def mock_astream(*args, **kwargs):
            raise ValueError("LLM Stream Failure")
            yield  # Make it a generator
            
        mock_instance.astream = mock_astream
        
        client = LlamaClient()
        with pytest.raises(HTTPException) as exc_info:
            async for _ in client.complete_stream("Fail prompt"):
                pass
        assert exc_info.value.status_code == 500
        await client.close()

@pytest.mark.asyncio
async def test_llama_client_embed_pytest_mode():
    """Embedding in pytest mode returns default mock values."""
    client = LlamaClient()
    result = await client.embed("test text")
    assert len(result) == 128
    assert result == [0.1] * 128
    await client.close()

@pytest.mark.asyncio
async def test_llama_client_embed_production_mode():
    """Patching sys.modules to test the actual LangChain embedding logic."""
    client = LlamaClient()
    client.embedding_url = "http://localhost:8080"
    
    original_pytest = sys.modules.pop("pytest", None)
    try:
        with patch("src.backend.core.engine.llm.OpenAIEmbeddings") as mock_openai_emb:
            mock_emb_instance = MagicMock()
            mock_openai_emb.return_value = mock_emb_instance
            mock_emb_instance.aembed_query = AsyncMock(return_value=[0.5] * 128)
            
            result = await client.embed("real embedding text")
            assert result == [0.5] * 128
            mock_emb_instance.aembed_query.assert_called_once_with("real embedding text")
            
            # Test exception branch
            mock_emb_instance.aembed_query.side_effect = RuntimeError("Emb fail")
            fail_result = await client.embed("fail text")
            assert fail_result is None
    finally:
        if original_pytest is not None:
            sys.modules["pytest"] = original_pytest
    await client.close()

@pytest.mark.asyncio
async def test_llama_client_health_check():
    """Verify health_check queries correct ports and processes mock results."""
    client = LlamaClient()
    client.url = "http://localhost:8080"
    client.embedding_url = "http://localhost:8081"
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    with patch.object(client.client, "get", AsyncMock(return_value=mock_response)) as mock_get:
        res = await client.health_check()
        assert res == {"inference": True, "embedding": True}
        assert mock_get.call_count == 2
        
        # Test failing responses
        mock_response.status_code = 500
        res = await client.health_check()
        assert res == {"inference": False, "embedding": False}
        
        # Test connection exceptions
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        res = await client.health_check()
        assert res == {"inference": False, "embedding": False}
    await client.close()
