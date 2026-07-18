"""Config-centralization / hardcoding-removal regression tests.

Locks in that host/port/context-size/cadence come from ONE source (settings /
runner) instead of drifting literals scattered across modules.
"""

from unittest.mock import MagicMock

from src.backend.core.config import settings
from src.backend.core.engine.runner import DEFAULT_CONFIG
from src.backend.core.engine.llm import LlamaClient


def test_context_size_is_16k_single_source():
    assert settings.CONTEXT_SIZE == 16384
    # runner's default inference context must not drift from settings.
    assert DEFAULT_CONFIG["inference"]["context_size"] == settings.CONTEXT_SIZE


def test_embedding_url_default_is_consolidated_port():
    # The runtime consolidated embeddings onto the inference port (8080); the
    # old :8081 default was dead drift.
    assert settings.EMBEDDING_SERVER_URL.endswith(":8080")


def test_reflection_interval_is_config_driven():
    assert (
        isinstance(settings.REFLECTION_INTERVAL, int)
        and settings.REFLECTION_INTERVAL > 0
    )


def test_testing_flag_is_single_source_of_truth():
    # settings.TESTING is the one place "are we under pytest" is decided; modules
    # read it instead of re-sniffing sys.modules. It must be True in this run.
    assert settings.TESTING is True


def test_llama_client_host_comes_from_settings(monkeypatch):
    monkeypatch.setattr(settings, "LLAMA_HOST", "10.11.12.13")
    client = LlamaClient()
    client.url = None  # force the derived (settings-based) path
    assert "10.11.12.13" in client.url
    assert "10.11.12.13" in client.embedding_url


def test_embeddings_fallback_uses_settings_url(monkeypatch):
    """When the llm_client exposes no embedding_url, the sync embedding path
    must fall back to settings.EMBEDDING_SERVER_URL, not a hardcoded :8081."""
    import asyncio
    from src.backend.core.memory.vector_store import LlamaCppEmbeddings

    monkeypatch.setattr(settings, "EMBEDDING_SERVER_URL", "http://fallback-host:9099")

    called = {}

    def fake_post(url, **kwargs):
        called["url"] = url
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"embedding": [0.1, 0.2]}
        return resp

    monkeypatch.setattr("httpx.post", fake_post)

    client = MagicMock(spec=[])  # no embedding_url attribute
    emb = LlamaCppEmbeddings(client)

    async def run():
        # embed_documents takes the sync-with-running-loop branch under a loop
        return emb.embed_documents(["hello"])

    asyncio.run(run())
    assert "fallback-host:9099" in called["url"]
