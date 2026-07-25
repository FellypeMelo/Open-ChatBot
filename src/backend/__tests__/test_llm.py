import pytest
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
    assert len(result) == 2560
    assert result == [0.1] * 2560
    await client.close()


@pytest.mark.asyncio
async def test_llama_client_embed_production_mode():
    """With settings.TESTING off, embed() runs the real LangChain path."""
    client = LlamaClient()
    client.embedding_url = "http://localhost:8080"

    with (
        patch.object(settings, "TESTING", False),
        patch.object(settings, "E2E_TESTING", False),
        patch("src.backend.core.engine.llm.OpenAIEmbeddings") as mock_openai_emb,
    ):
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
    await client.close()


def test_get_chat_llm_reuses_cached_client_for_same_target():
    """Same (base_url, model, timeout) must return the identical ChatOpenAI
    instance, not construct a fresh one."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_chat_openai.side_effect = lambda **kwargs: MagicMock()

        client = LlamaClient()
        first = client._get_chat_llm(
            "http://host:8080/v1", "model-a", settings.LLM_TIMEOUT
        )
        second = client._get_chat_llm(
            "http://host:8080/v1", "model-a", settings.LLM_TIMEOUT
        )

        assert first is second
        mock_chat_openai.assert_called_once()


def test_get_chat_llm_builds_new_client_for_different_base_url_or_model():
    """A different base_url or model must never reuse a cached client -- that
    would silently route a request to the wrong server/model."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_chat_openai.side_effect = lambda **kwargs: MagicMock()

        client = LlamaClient()
        same = client._get_chat_llm(
            "http://host-a:8080/v1", "model-a", settings.LLM_TIMEOUT
        )
        different_url = client._get_chat_llm(
            "http://host-b:8080/v1", "model-a", settings.LLM_TIMEOUT
        )
        different_model = client._get_chat_llm(
            "http://host-a:8080/v1", "model-b", settings.LLM_TIMEOUT
        )

        assert same is not different_url
        assert same is not different_model
        assert different_url is not different_model
        assert mock_chat_openai.call_count == 3


@pytest.mark.asyncio
async def test_llm_complete_reuses_cached_client_but_sends_fresh_sampler_kwargs():
    """complete() must reuse the same cached ChatOpenAI client across calls to
    the same target, while still passing each call's own preset-derived sampler
    settings (temperature/top_p/extra_body) fresh to ainvoke() -- caching the
    client must not freeze stale sampler values from whichever preset built it
    first."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        mock_instance.ainvoke = AsyncMock(return_value=MagicMock(content="ok"))

        client = LlamaClient()
        await client.complete(
            "p1",
            url="http://host:8080",
            model="model-a",
            preset={"temperature": 0.1, "top_p": 0.2},
        )
        await client.complete(
            "p2",
            url="http://host:8080",
            model="model-a",
            preset={"temperature": 0.9, "top_p": 0.8},
        )

        mock_chat_openai.assert_called_once()
        assert mock_instance.ainvoke.call_count == 2
        first_kwargs = mock_instance.ainvoke.call_args_list[0].kwargs
        second_kwargs = mock_instance.ainvoke.call_args_list[1].kwargs
        assert first_kwargs["temperature"] == 0.1
        assert first_kwargs["top_p"] == 0.2
        assert second_kwargs["temperature"] == 0.9
        assert second_kwargs["top_p"] == 0.8
        await client.close()


@pytest.mark.asyncio
async def test_llm_complete_builds_separate_clients_for_different_targets():
    """complete() calls against different urls/models must each be built with
    their own base_url/model_name -- a cache hit must never send a request
    meant for one server/model to another."""
    with patch("src.backend.core.engine.llm.ChatOpenAI") as mock_chat_openai:
        mock_chat_openai.side_effect = lambda **kwargs: MagicMock(
            ainvoke=AsyncMock(return_value=MagicMock(content="ok"))
        )

        client = LlamaClient()
        await client.complete("p", url="http://host-a:8080", model="model-a")
        await client.complete("p", url="http://host-b:8080", model="model-a")
        await client.complete("p", url="http://host-a:8080", model="model-b")

        assert mock_chat_openai.call_count == 3
        called_targets = [
            (call.kwargs["base_url"], call.kwargs["model_name"])
            for call in mock_chat_openai.call_args_list
        ]
        assert called_targets == [
            ("http://host-a:8080/v1", "model-a"),
            ("http://host-b:8080/v1", "model-a"),
            ("http://host-a:8080/v1", "model-b"),
        ]
        await client.close()


def test_get_embeddings_client_reuses_cached_client_for_same_target():
    with patch("src.backend.core.engine.llm.OpenAIEmbeddings") as mock_openai_emb:
        mock_openai_emb.side_effect = lambda **kwargs: MagicMock()

        client = LlamaClient()
        first = client._get_embeddings_client("http://host:8080/v1", "model-a")
        second = client._get_embeddings_client("http://host:8080/v1", "model-a")
        different = client._get_embeddings_client("http://host:8080/v1", "model-b")

        assert first is second
        assert first is not different
        assert mock_openai_emb.call_count == 2


@pytest.mark.asyncio
async def test_llama_client_health_check():
    """Verify health_check queries correct ports and processes mock results."""
    client = LlamaClient()
    client.url = "http://localhost:8080"
    client.embedding_url = "http://localhost:8081"

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch.object(
        client.client, "get", AsyncMock(return_value=mock_response)
    ) as mock_get:
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
