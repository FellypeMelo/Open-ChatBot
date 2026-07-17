"""Per-chat (Chat/Session entity) scoping tests -- the user's core concern:
memory/history must be linked to (character, chat) so a new chat can't poison
another. Covers specs T1-T5 from docs/app-analysis-and-rp-plan.md.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import AgentState, Character, MessageNode, Chat, JournalEntry


# --- T1: per-chat memory isolation via the chat_id metadata filter -----------

class _FakeLLM:
    """Deterministic embeddings so a real turbovec store can be exercised
    without a llama-server: the vector only depends on the text."""

    async def embed(self, text):
        vec = [0.1] * 8
        vec[sum(map(ord, text)) % 8] = 1.0
        return vec


def test_query_memory_is_isolated_by_chat_id(tmp_path):
    vs = VectorStore(llm_client=_FakeLLM(), path=str(tmp_path / "cdb"))

    asyncio.run(
        vs.add_memory("User: I love pirates", {"character_id": 1, "chat_id": 10})
    )
    asyncio.run(
        vs.add_memory("User: I love baking", {"character_id": 1, "chat_id": 20})
    )

    # Query chat 20 only. min_relevance=-1.0 isolates the chat_id filter from the
    # similarity threshold, so the ONLY thing excluding the pirates memory is
    # that it belongs to chat 10.
    out = asyncio.run(
        vs.query_memory(
            "tell me about pirates",
            metadata_filter={"character_id": 1, "chat_id": 20},
            min_relevance=-1.0,
        )
    )
    docs = out["documents"][0]
    assert any("baking" in d for d in docs)
    assert all("pirates" not in d for d in docs), "chat 10 memory leaked into chat 20"


# --- T4: delete a chat removes only its own memories -------------------------

class _FakeStore:
    def __init__(self, docs=None):
        self._docs = dict(docs or {})
        self.dumped = False

    def delete(self, ids):
        for i in ids:
            self._docs.pop(i, None)

    def dump(self, path):
        self.dumped = True


def test_clear_chat_memories_removes_only_that_chat(tmp_path):
    vs = VectorStore(llm_client=MagicMock(), path=str(tmp_path / "cdb"))
    vs.memories_store = _FakeStore(
        {
            "m1": ("pirates", {"character_id": 1, "chat_id": 10}),
            "m2": ("more pirates", {"character_id": 1, "chat_id": 10}),
            "m3": ("baking", {"character_id": 1, "chat_id": 20}),
        }
    )
    removed = asyncio.run(vs.clear_chat_memories(10))

    assert removed == 2
    remaining = {meta.get("chat_id") for _t, meta in vs.memories_store._docs.values()}
    assert 10 not in remaining
    assert 20 in remaining
    assert vs.memories_store.dumped is True


# --- T2: 'New Chat' creates a session instead of deleting history ------------

def test_new_chat_preserves_history_and_switches_active(client, db_session):
    char = Character(id=701, name="SessChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=701)
    db_session.add(state)
    db_session.commit()

    first_chat = Chat(character_id=701, title="Chat A")
    db_session.add(first_chat)
    db_session.commit()
    state.active_chat_id = first_chat.id
    for i in range(3):
        db_session.add(
            MessageNode(
                character_id=701,
                chat_id=first_chat.id,
                role="user",
                content=f"m{i}",
            )
        )
    db_session.commit()

    resp = client.post("/chat/new/701")
    assert resp.status_code == 200
    new_chat_id = resp.json()["chat_id"]
    assert new_chat_id != first_chat.id

    # The original 3 messages must still exist -- new chat is non-destructive.
    assert (
        db_session.query(MessageNode).filter(MessageNode.chat_id == first_chat.id).count()
        == 3
    )
    # There are now two chats and the new one is active.
    chats = client.get("/chats/701").json()
    assert len(chats) == 2
    active = [c for c in chats if c["is_active"]]
    assert len(active) == 1 and active[0]["id"] == new_chat_id
    db_session.refresh(state)
    assert state.active_chat_id == new_chat_id


# --- T3: delete_character purges messages/journals/memories ------------------

def test_delete_character_purges_all_data_and_memories(client, db_session):
    char = Character(id=702, name="DoomedChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=702)
    db_session.add(state)
    db_session.commit()
    chat = Chat(character_id=702, title="C")
    db_session.add(chat)
    db_session.commit()
    db_session.add_all(
        [
            MessageNode(character_id=702, chat_id=chat.id, role="user", content="a"),
            MessageNode(character_id=702, chat_id=chat.id, role="assistant", content="b"),
            JournalEntry(character_id=702, chat_id=chat.id, content="diary"),
        ]
    )
    db_session.commit()

    fake_vs = MagicMock()
    fake_vs.clear_character_memories = AsyncMock(return_value=2)
    with patch("src.backend.api.characters.vector_store", fake_vs):
        resp = client.delete("/characters/702")
    assert resp.status_code == 200

    assert db_session.query(MessageNode).filter(MessageNode.character_id == 702).count() == 0
    assert db_session.query(JournalEntry).filter(JournalEntry.character_id == 702).count() == 0
    assert db_session.query(Chat).filter(Chat.character_id == 702).count() == 0
    assert db_session.query(AgentState).filter(AgentState.character_id == 702).first() is None
    fake_vs.clear_character_memories.assert_awaited_once_with(702)


# --- T5: parent_id from another character/chat is rejected -------------------

def test_parent_id_from_other_character_is_rejected(client, db_session):
    # Character 1 / chat 10 with its own message; Character 2 / chat 20 with a
    # foreign message we will try to graft onto character 1's turn.
    c1 = Character(id=703, name="C1", description="d")
    c2 = Character(id=704, name="C2", description="d")
    db_session.add_all([c1, c2])
    db_session.commit()
    s1 = AgentState(character_id=703)
    db_session.add(s1)
    db_session.commit()
    chat1 = Chat(character_id=703, title="c1")
    chat2 = Chat(character_id=704, title="c2")
    db_session.add_all([chat1, chat2])
    db_session.commit()
    s1.active_chat_id = chat1.id
    own = MessageNode(character_id=703, chat_id=chat1.id, role="user", content="mine")
    foreign = MessageNode(
        character_id=704, chat_id=chat2.id, role="user", content="FOREIGN SECRET"
    )
    db_session.add_all([own, foreign])
    db_session.commit()
    s1.current_message_id = own.id
    db_session.commit()

    captured = {}

    async def fake_build_prompt(user_message, character, state_dict, **kwargs):
        captured["history"] = kwargs.get("history") or []
        return "PROMPT"

    with patch(
        "src.backend.api.chat.brain.build_prompt",
        new=AsyncMock(side_effect=fake_build_prompt),
    ), patch(
        "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = {"content": "ok."}
        resp = client.post(
            "/chat",
            json={"character_id": 703, "chat_id": chat1.id, "message": "hi", "parent_id": foreign.id},
        )
    assert resp.status_code == 200
    # The foreign character's line must never enter character 1's prompt history.
    assert all(
        "FOREIGN SECRET" not in (m.get("content") or "") for m in captured["history"]
    ), "cross-character parent_id grafted foreign message into the prompt"
