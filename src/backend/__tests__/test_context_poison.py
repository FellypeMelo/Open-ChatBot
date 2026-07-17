"""Regression tests for RAG context poisoning.

Reproduces the bug where a character's hallucinated/old replies were stored as
vector memories and then re-injected into every prompt (even an unrelated
"hello"), because:
  1. query_memory returned the top-k memories with NO relevance threshold, and
  2. clear_chat_history purged messages/journal but left the vector store intact.

These tests use lightweight fakes so they are fully isolated (no llama-server,
no real embeddings, no production DB).
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.backend.core.memory.vector_store import VectorStore


class _FakeStore:
    """Minimal stand-in for TurboQuantVectorStore: just the surface our
    VectorStore wrapper touches (_docs, delete, dump)."""

    def __init__(self, docs=None):
        # id -> (text, metadata)
        self._docs = dict(docs or {})
        self.dumped = False

    def delete(self, ids):
        for i in ids:
            self._docs.pop(i, None)

    def dump(self, path):
        self.dumped = True


def _make_vs(tmp_path):
    vs = VectorStore(llm_client=MagicMock(), path=str(tmp_path / "cdb"))
    vs.memories_store = _FakeStore()
    return vs


def test_clear_character_memories_removes_only_that_character(tmp_path):
    vs = _make_vs(tmp_path)
    vs.memories_store = _FakeStore(
        {
            "m1": ("User: hi\nAI: We danced at the Baile ballroom", {"character_id": 1}),
            "m2": ("User: hi\nAI: tuxedo again", {"character_id": 1}),
            "m3": ("memory belonging to a different character", {"character_id": 2}),
        }
    )
    removed = asyncio.run(vs.clear_character_memories(1))

    assert removed == 2
    remaining = {cid for _t, meta in vs.memories_store._docs.values() for cid in [meta.get("character_id")]}
    assert 1 not in remaining
    assert 2 in remaining
    assert vs.memories_store.dumped is True


def test_clear_by_metadata_surfaces_persist_failure(tmp_path):
    """A dump() failure during a purge must propagate, not be swallowed as a
    silent 0 (PZ-03). Otherwise the endpoint reports 'cleared' while the on-disk
    store still holds the memories, which resurface after a restart."""
    vs = _make_vs(tmp_path)
    vs.memories_store = _FakeStore({"m1": ("secret", {"chat_id": 9})})

    def _boom(_path):
        raise OSError("disk full")

    vs.memories_store.dump = _boom

    with pytest.raises(OSError):
        asyncio.run(vs.clear_chat_memories(9))


def test_delete_by_message_ids_removes_only_matching(tmp_path):
    """Memories tied to edited/deleted/regenerated-away message nodes must be
    removable by their assistant message id, so discarded content stops being
    retrievable via RAG (PZ-01)."""
    vs = _make_vs(tmp_path)
    vs.memories_store = _FakeStore(
        {
            "d1": ("turn A", {"character_id": 1, "message_id": 10}),
            "d2": ("turn B", {"character_id": 1, "message_id": 11}),
            "d3": ("legacy, no id", {"character_id": 1}),
        }
    )

    removed = asyncio.run(vs.delete_by_message_ids([10]))

    assert removed == 1
    remaining = [meta.get("message_id") for _t, meta in vs.memories_store._docs.values()]
    assert 10 not in remaining
    assert 11 in remaining
    assert vs.memories_store.dumped is True


def test_query_memory_drops_results_below_relevance_threshold(tmp_path):
    vs = _make_vs(tmp_path)
    high = (Document(id="a", page_content="genuinely relevant memory", metadata={}), 0.82)
    low = (Document(id="b", page_content="Baile ballroom poison", metadata={}), 0.06)
    vs.memories_store.asimilarity_search_with_score = AsyncMock(return_value=[high, low])

    out = asyncio.run(vs.query_memory("hello", min_relevance=0.5))
    docs = out["documents"][0]

    assert "genuinely relevant memory" in docs
    assert all("poison" not in d for d in docs), "irrelevant memory leaked past the threshold"


def test_query_memory_prefers_recent_on_similar_scores(tmp_path):
    # RQ-01: with near-equal relevance, the more recent memory (higher
    # message_id) should rank first, so the character doesn't forget 'now'.
    vs = _make_vs(tmp_path)
    old = (Document(id="o", page_content="OLD memory", metadata={"message_id": 1}), 0.80)
    new = (Document(id="n", page_content="NEW memory", metadata={"message_id": 500}), 0.80)
    vs.memories_store.asimilarity_search_with_score = AsyncMock(return_value=[old, new])

    out = asyncio.run(vs.query_memory("q", n_results=2, min_relevance=0.5))
    docs = out["documents"][0]

    assert docs[0] == "NEW memory"
    assert "OLD memory" in docs


def test_query_memory_drops_near_duplicate_results(tmp_path):
    # RQ-03: near-identical memories (e.g. repeated paraphrases of one moment)
    # must not fill the top-k; only one representative is kept.
    vs = _make_vs(tmp_path)
    dup_a = (Document(id="a", page_content="We danced at the ballroom tonight", metadata={"message_id": 5}), 0.9)
    dup_b = (Document(id="b", page_content="We danced at the ballroom tonight.", metadata={"message_id": 6}), 0.89)
    other = (Document(id="c", page_content="You told me about your dog", metadata={"message_id": 7}), 0.7)
    vs.memories_store.asimilarity_search_with_score = AsyncMock(
        return_value=[dup_a, dup_b, other]
    )

    out = asyncio.run(vs.query_memory("q", n_results=5, min_relevance=0.5))
    docs = out["documents"][0]

    ballroom = [d for d in docs if "ballroom" in d]
    assert len(ballroom) == 1
    assert any("dog" in d for d in docs)


def test_clear_chat_history_purges_vector_memory():
    """The clear-chat endpoint must purge the character's vector memories,
    otherwise 'New Chat' still resurfaces old/hallucinated content via RAG."""
    import src.backend.api.chat as chatmod

    fake_vs = MagicMock()
    fake_vs.clear_character_memories = AsyncMock(return_value=3)

    db = MagicMock()
    state = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = state

    with patch.object(chatmod, "vector_store", fake_vs):
        asyncio.run(chatmod.clear_chat_history(7, db=db))

    fake_vs.clear_character_memories.assert_awaited_once_with(7)
    # active_summary must also be wiped so summary-based poison cannot survive.
    assert state.active_summary == ""


def test_e2e_and_pytest_isolate_the_vector_store_path():
    """E2E/unit runs must NOT use the real ./chroma_db, otherwise mock test
    memories leak into real chats (the root cause of the Baile/Ballroom poison)."""
    from src.backend.core.config import Settings

    e2e = Settings(E2E_TESTING=True)
    assert e2e.CHROMA_PATH != "./chroma_db"
    assert "e2e" in e2e.CHROMA_PATH.lower()
    assert e2e.DATABASE_URL == "sqlite:///./e2e_test.db"

    # This process is pytest, so even a plain Settings() must avoid the real store.
    default = Settings()
    assert default.CHROMA_PATH != "./chroma_db"
