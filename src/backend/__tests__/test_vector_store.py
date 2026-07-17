import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.backend.core.memory.vector_store import VectorStore, LlamaCppEmbeddings


@pytest.mark.asyncio
async def test_llama_cpp_embeddings_sync_with_loop(monkeypatch):
    # Test LlamaCppEmbeddings.embed_documents when an event loop is running
    mock_llm = AsyncMock()
    mock_llm.embedding_url = "http://mock-url"

    embeddings = LlamaCppEmbeddings(mock_llm)

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    # Mock httpx.post
    mock_post = MagicMock()
    monkeypatch.setattr("httpx.post", mock_post)

    # 1. Success with array of embeddings
    mock_post.return_value = MockResponse(200, [{"embedding": [0.1, 0.2]}])
    res = embeddings.embed_documents(["hello"])
    assert res == [[0.1, 0.2]]

    # 2. Success with direct dictionary
    mock_post.return_value = MockResponse(200, {"embedding": [0.3, 0.4]})
    res = embeddings.embed_documents(["hello"])
    assert res == [[0.3, 0.4]]

    # 3. Success but unexpected format
    mock_post.return_value = MockResponse(200, "not a dict")
    res = embeddings.embed_documents(["hello"])
    assert res == [[]]

    # 4. Status code not 200
    mock_post.return_value = MockResponse(500, {})
    res = embeddings.embed_documents(["hello"])
    assert res == [[]]

    # 5. Exception raised
    mock_post.side_effect = Exception("HTTP Error")
    res = embeddings.embed_documents(["hello"])
    assert res == [[]]


@pytest.mark.asyncio
async def test_llama_cpp_embeddings_methods():
    mock_llm = AsyncMock()
    mock_llm.embed.side_effect = lambda t: [0.1] if t == "test" else None

    embeddings = LlamaCppEmbeddings(mock_llm)

    # embed_query should call embed_documents
    with patch.object(embeddings, "embed_documents", return_value=[[0.5]]) as mock_emb:
        assert embeddings.embed_query("test") == [0.5]
        mock_emb.assert_called_once_with(["test"])

    with patch.object(embeddings, "embed_documents", return_value=[]) as mock_emb:
        assert embeddings.embed_query("test") == []

    # aembed_documents must NOT silently drop a failed embedding -- that would
    # misalign text<->metadata in a batch add. It raises so the caller aborts
    # the whole add instead (SEC-03).
    with pytest.raises(ValueError):
        await embeddings.aembed_documents(["test", "fail"])
    # All-successful stays 1:1 and ordered.
    assert await embeddings.aembed_documents(["test", "test"]) == [[0.1], [0.1]]

    # aembed_query
    assert await embeddings.aembed_query("test") == [0.1]
    assert await embeddings.aembed_query("fail") == []


@pytest.mark.asyncio
async def test_vector_store_disk_loading(tmp_path):
    test_path = tmp_path / "test_store_loading"
    mem_path = test_path / "memories"
    lore_path = test_path / "lorebooks"

    mem_path.mkdir(parents=True)
    (mem_path / "index.tvim").touch()

    lore_path.mkdir(parents=True)
    (lore_path / "index.tvim").touch()

    mock_llm = AsyncMock()

    # Test load failure and exception handling
    with patch(
        "turbovec.langchain.TurboQuantVectorStore.load",
        side_effect=Exception("Load error"),
    ):
        store = VectorStore(llm_client=mock_llm, path=str(test_path))
        assert store.memories_store is not None
        assert store.lore_store is not None

    # Test load success
    mock_store_loaded = MagicMock()
    with patch(
        "turbovec.langchain.TurboQuantVectorStore.load", return_value=mock_store_loaded
    ):
        store = VectorStore(llm_client=mock_llm, path=str(test_path))
        assert store.memories_store == mock_store_loaded
        assert store.lore_store == mock_store_loaded


@pytest.mark.asyncio
async def test_vector_store_lore_operations(tmp_path):
    test_path = tmp_path / "test_store_lore"
    mock_llm = AsyncMock()

    # 1. Add lore fail - embedding is None
    mock_llm.embed.return_value = None
    store = VectorStore(llm_client=mock_llm, path=str(test_path))
    await store.add_lore("key", "val")

    # 2. Add lore success
    mock_llm.embed.return_value = [0.1] * 128

    mock_lore_store = MagicMock()
    store.lore_store = mock_lore_store

    await store.add_lore("key", "val", metadata={"src": "test"})
    mock_lore_store._store_texts_and_vectors.assert_called_once()
    mock_lore_store.dump.assert_called_once()

    # 3. Add lore exception
    mock_lore_store._store_texts_and_vectors.side_effect = Exception("Write error")
    # Should not raise exception, just log it
    await store.add_lore("key", "val")

    # 4. Query lore empty keywords
    res = await store.query_lore([])
    assert res == {"documents": [[]]}

    # 5. Query lore success
    mock_doc = MagicMock()
    mock_doc.page_content = "lore_content"
    mock_lore_store.asimilarity_search_with_score = AsyncMock(
        return_value=[(mock_doc, 0.9)]
    )

    res = await store.query_lore(["key1", "key2"])
    assert res == {"documents": [["lore_content"]]}

    # 5b. SEC-05: a below-threshold (irrelevant) nearest neighbor is dropped.
    low_doc = MagicMock()
    low_doc.page_content = "irrelevant"
    mock_lore_store.asimilarity_search_with_score = AsyncMock(
        return_value=[(low_doc, 0.2)]
    )
    res = await store.query_lore(["unrelated"])
    assert res == {"documents": [[]]}

    # 6. Query lore exception
    mock_lore_store.asimilarity_search_with_score.side_effect = Exception("Query error")
    res = await store.query_lore(["key"])
    assert res == {"documents": [[]]}


@pytest.mark.asyncio
async def test_llama_cpp_embeddings_sync_no_loop(monkeypatch):
    # Test LlamaCppEmbeddings.embed_documents when no event loop is running
    mock_llm = AsyncMock()
    embeddings = LlamaCppEmbeddings(mock_llm)

    # Mock asyncio.get_running_loop to raise RuntimeError
    mock_get_loop = MagicMock(side_effect=RuntimeError("No loop"))
    monkeypatch.setattr(asyncio, "get_running_loop", mock_get_loop)

    # Mock asyncio.run to just call aembed_documents synchronously
    mock_run = MagicMock(return_value=[[0.7, 0.8]])
    monkeypatch.setattr(asyncio, "run", mock_run)

    res = embeddings.embed_documents(["hello"])
    assert res == [[0.7, 0.8]]
    mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_vector_store_memory_operations(tmp_path):
    test_path = tmp_path / "test_store_mem_ops"
    mock_llm = AsyncMock()
    store = VectorStore(llm_client=mock_llm, path=str(test_path))

    # 1. Add memory success
    mock_mem_store = MagicMock()
    mock_mem_store.aadd_texts = AsyncMock()
    store.memories_store = mock_mem_store

    await store.add_memory("hello", metadata={"test": True})
    mock_mem_store.aadd_texts.assert_called_once_with(
        ["hello"], metadatas=[{"test": True}]
    )
    mock_mem_store.dump.assert_called_once()

    # 2. Add memory exception
    mock_mem_store.aadd_texts.side_effect = Exception("Add error")
    await store.add_memory("hello")  # should handle internally

    # 3. Query memory success
    mock_doc = MagicMock()
    mock_doc.page_content = "mem_content"
    mock_mem_store.asimilarity_search_with_score = AsyncMock(
        return_value=[(mock_doc, 0.85)]
    )

    res = await store.query_memory(
        "query", n_results=3, metadata_filter={"user": "123"}
    )
    assert res == {"documents": [["mem_content"]]}
    # Over-fetches n_results*4 candidates so the recency re-rank has room (RQ-01).
    mock_mem_store.asimilarity_search_with_score.assert_called_once_with(
        "query", k=12, filter={"user": "123"}
    )

    # 4. Query memory exception
    mock_mem_store.asimilarity_search_with_score.side_effect = Exception("Search error")
    res = await store.query_memory("hello")
    assert res == {"documents": [[]]}


class _FakeLLM:
    """Deterministic 8-dim embeddings so a real turbovec store persists to disk
    without a llama-server."""

    async def embed(self, text):
        vec = [0.1] * 8
        vec[sum(map(ord, text)) % 8] = 1.0
        return vec


def test_atomic_dump_failure_does_not_corrupt_persisted_store(tmp_path):
    # PF-02: turbovec.dump writes multiple files directly into the store dir; a
    # crash mid-dump would corrupt the only persisted copy. _atomic_dump stages
    # into a temp dir and swaps atomically, so a failing dump leaves the prior
    # on-disk store fully intact and reloadable.
    path = str(tmp_path / "cdb")
    vs = VectorStore(llm_client=_FakeLLM(), path=path)

    asyncio.run(vs.add_memory("first memory", {"character_id": 1}))

    # A dump that raises must NOT damage the persisted store nor leave a temp dir.
    with patch.object(
        vs.memories_store, "dump", side_effect=IOError("simulated disk failure")
    ):
        asyncio.run(vs.add_memory("second memory", {"character_id": 1}))

    assert not (vs.memories_path.parent / "memories.tmp").exists(), "temp dir leaked"

    reloaded = VectorStore(llm_client=_FakeLLM(), path=path)
    texts = [t for t, _m in reloaded.memories_store._docs.values()]
    assert any("first memory" in t for t in texts), "prior store lost after failed dump"
    assert all(
        "second memory" not in t for t in texts
    ), "half-written store persisted the failed add"


def test_atomic_dump_persists_and_reloads(tmp_path):
    # Happy path: an atomic dump round-trips through disk correctly.
    path = str(tmp_path / "cdb")
    vs = VectorStore(llm_client=_FakeLLM(), path=path)
    asyncio.run(vs.add_memory("hello world", {"character_id": 7}))

    reloaded = VectorStore(llm_client=_FakeLLM(), path=path)
    texts = [t for t, _m in reloaded.memories_store._docs.values()]
    assert any("hello world" in t for t in texts)
    assert not (vs.memories_path.parent / "memories.tmp").exists()


class _FakeLLMWithComplete:
    """Deterministic embeddings + a mockable complete() for consolidation."""

    def __init__(self, summary="CONDENSED SUMMARY", fail=False):
        self._summary = summary
        self._fail = fail
        self.complete_calls = 0

    async def embed(self, text):
        vec = [0.1] * 8
        vec[sum(map(ord, text)) % 8] = 1.0
        return vec

    async def complete(self, prompt, **kwargs):
        self.complete_calls += 1
        if self._fail:
            raise RuntimeError("llm unavailable")
        return {"content": self._summary}


def _scope(vs, character_id, chat_id):
    return [
        (t, m)
        for t, m in vs.memories_store._docs.values()
        if m.get("character_id") == character_id and m.get("chat_id") == chat_id
    ]


def test_memory_consolidation_condenses_oldest_when_capped(tmp_path, monkeypatch):
    # RQ-05: exceeding the cap folds the oldest batch into one consolidated
    # memory, leaving recent memories intact.
    from src.backend.core.config import settings

    monkeypatch.setattr(settings, "MEMORY_STORE_CAP", 5)
    monkeypatch.setattr(settings, "MEMORY_CONSOLIDATE_BATCH", 3)
    llm = _FakeLLMWithComplete()
    vs = VectorStore(llm_client=llm, path=str(tmp_path / "cdb"))

    async def run():
        for i in range(6):
            await vs.add_memory(
                f"User: msg {i}\nAI: reply {i}",
                {"character_id": 1, "chat_id": 10, "message_id": i + 1},
            )

    asyncio.run(run())

    scope = _scope(vs, 1, 10)
    assert len(scope) == 4, "should be 6 - 3 oldest + 1 consolidated"
    assert llm.complete_calls == 1
    assert any(m.get("consolidated") for _t, m in scope)
    assert any("CONDENSED SUMMARY" in t for t, _m in scope)
    # The most recent originals survive full-fidelity.
    assert any("reply 5" in t for t, _m in scope)


def test_consolidation_is_scoped_and_spares_other_chats(tmp_path, monkeypatch):
    from src.backend.core.config import settings

    monkeypatch.setattr(settings, "MEMORY_STORE_CAP", 5)
    monkeypatch.setattr(settings, "MEMORY_CONSOLIDATE_BATCH", 3)
    llm = _FakeLLMWithComplete()
    vs = VectorStore(llm_client=llm, path=str(tmp_path / "cdb"))

    async def run():
        for i in range(6):
            await vs.add_memory(
                f"chat10 msg {i}", {"character_id": 1, "chat_id": 10, "message_id": i + 1}
            )
        for i in range(2):
            await vs.add_memory(
                f"chat20 msg {i}", {"character_id": 1, "chat_id": 20, "message_id": i + 1}
            )

    asyncio.run(run())

    assert len(_scope(vs, 1, 20)) == 2, "a different chat's memories must be untouched"


def test_consolidation_failure_keeps_originals(tmp_path, monkeypatch):
    # A failed summarize must NOT delete the batch (no data loss without a
    # replacement in hand).
    from src.backend.core.config import settings

    monkeypatch.setattr(settings, "MEMORY_STORE_CAP", 5)
    monkeypatch.setattr(settings, "MEMORY_CONSOLIDATE_BATCH", 3)
    llm = _FakeLLMWithComplete(fail=True)
    vs = VectorStore(llm_client=llm, path=str(tmp_path / "cdb"))

    async def run():
        for i in range(6):
            await vs.add_memory(
                f"User: msg {i}\nAI: reply {i}",
                {"character_id": 1, "chat_id": 10, "message_id": i + 1},
            )

    asyncio.run(run())

    assert len(_scope(vs, 1, 10)) == 6, "failed consolidation must not drop memories"
    assert llm.complete_calls == 1


class _FakeLLMEmbedFailsOnSummary:
    """Embeds every text EXCEPT the consolidated summary, which fails -- models a
    transient embedding-server hiccup on the consolidation add step."""

    def __init__(self, summary="CONDENSED SUMMARY"):
        self._summary = summary
        self.complete_calls = 0

    async def embed(self, text):
        if text == self._summary:
            return None
        vec = [0.1] * 8
        vec[sum(map(ord, text)) % 8] = 1.0
        return vec

    async def complete(self, prompt, **kwargs):
        self.complete_calls += 1
        return {"content": self._summary}


def test_consolidation_add_failure_keeps_originals(tmp_path, monkeypatch):
    # RQ-05 (P2): summarize succeeds but STORING the consolidated memory fails
    # (embedding-server hiccup on the add step). The oldest batch must NOT be
    # lost -- the store must happen before the delete, never the reverse.
    from src.backend.core.config import settings

    monkeypatch.setattr(settings, "MEMORY_STORE_CAP", 5)
    monkeypatch.setattr(settings, "MEMORY_CONSOLIDATE_BATCH", 3)
    llm = _FakeLLMEmbedFailsOnSummary()
    vs = VectorStore(llm_client=llm, path=str(tmp_path / "cdb"))

    async def run():
        for i in range(6):
            await vs.add_memory(
                f"User: msg {i}\nAI: reply {i}",
                {"character_id": 1, "chat_id": 10, "message_id": i + 1},
            )

    asyncio.run(run())

    # 6 originals must all survive; none consolidated away without a replacement.
    scope = _scope(vs, 1, 10)
    assert len(scope) == 6, "batch was deleted before its replacement was stored"
    assert all(not m.get("consolidated") for _t, m in scope)
