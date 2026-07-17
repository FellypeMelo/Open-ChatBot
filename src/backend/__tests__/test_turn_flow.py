"""Turn-flow / message-tree integrity tests (F5). These target concrete tree
corruption failure modes in edit/delete/persist. All isolated: no llama-server,
no real DB, no vector store (vector_store is patched to an AsyncMock).
"""

import asyncio
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.pool import StaticPool

from src.backend.api.chat import (
    edit_message,
    delete_message,
    MessageEditRequest,
    ChatTurnContext,
    LLMConfig,
    _persist_assistant_reply,
)
from src.backend.db.database import Base
from src.backend.db.models import AgentState, Character, MessageNode, Chat, User


def _char_with_two_chats(db):
    """A character whose AgentState is live on chat A, with a second background
    chat B. Returns (char, state, chatA, chatB)."""
    char = Character(name="TF", description="d")
    db.add(char)
    db.commit()
    state = AgentState(character_id=char.id)
    db.add(state)
    db.commit()
    chat_a = Chat(character_id=char.id, title="A")
    chat_b = Chat(character_id=char.id, title="B")
    db.add_all([chat_a, chat_b])
    db.commit()
    state.active_chat_id = chat_a.id
    db.commit()
    return char, state, chat_a, chat_b


# --- TF-02: edit/delete must not corrupt a non-active chat's pointer ----------

def test_edit_in_background_chat_does_not_corrupt_active_pointer(db_session):
    # TF-02 (P1): editing a user message in a background chat set the LIVE
    # AgentState.current_message_id to that message, silently moving the
    # foreground chat's resume point to a message in a different chat.
    char, state, chat_a, chat_b = _char_with_two_chats(db_session)

    node_a = MessageNode(
        character_id=char.id, chat_id=chat_a.id, role="assistant", content="a-reply"
    )
    user_b = MessageNode(
        character_id=char.id, chat_id=chat_b.id, role="user", content="old B"
    )
    db_session.add_all([node_a, user_b])
    db_session.commit()
    state.current_message_id = node_a.id
    chat_b.current_message_id = user_b.id
    db_session.commit()

    with patch("src.backend.api.chat.vector_store") as vs:
        vs.delete_by_message_ids = AsyncMock()
        asyncio.run(
            edit_message(
                user_b.id, MessageEditRequest(content="edited B"), db=db_session
            )
        )

    db_session.refresh(state)
    db_session.refresh(chat_b)
    assert (
        state.current_message_id == node_a.id
    ), "active chat A pointer corrupted by an edit made in background chat B"
    assert (
        chat_b.current_message_id == user_b.id
    ), "background chat B should resume at its own edited message"


def test_edit_in_active_chat_still_repoints_live_state(db_session):
    # The active-chat path must keep working: editing a user message in the live
    # chat repoints the AgentState mirror so a regenerate forks from there.
    char, state, chat_a, chat_b = _char_with_two_chats(db_session)
    user_a = MessageNode(
        character_id=char.id, chat_id=chat_a.id, role="user", content="old A"
    )
    db_session.add(user_a)
    db_session.commit()
    state.current_message_id = 999  # some deeper node
    db_session.commit()

    with patch("src.backend.api.chat.vector_store") as vs:
        vs.delete_by_message_ids = AsyncMock()
        asyncio.run(
            edit_message(
                user_a.id, MessageEditRequest(content="edited A"), db=db_session
            )
        )

    db_session.refresh(state)
    assert state.current_message_id == user_a.id


def test_delete_current_message_in_background_chat_repoints_that_chat(db_session):
    # TF-02 (P1): deleting the current message of a background chat must repoint
    # THAT chat to the parent, not leave it dangling at a deactivated node, and
    # must not touch the active chat's live pointer.
    char, state, chat_a, chat_b = _char_with_two_chats(db_session)

    node_a = MessageNode(
        character_id=char.id, chat_id=chat_a.id, role="assistant", content="a-reply"
    )
    parent_b = MessageNode(
        character_id=char.id, chat_id=chat_b.id, role="user", content="parent B"
    )
    db_session.add_all([node_a, parent_b])
    db_session.commit()
    leaf_b = MessageNode(
        character_id=char.id,
        chat_id=chat_b.id,
        role="assistant",
        content="leaf B",
        parent_id=parent_b.id,
    )
    db_session.add(leaf_b)
    db_session.commit()
    state.current_message_id = node_a.id
    chat_b.current_message_id = leaf_b.id
    db_session.commit()

    with patch("src.backend.api.chat.vector_store") as vs:
        vs.delete_by_message_ids = AsyncMock()
        asyncio.run(delete_message(leaf_b.id, db=db_session))

    db_session.refresh(state)
    db_session.refresh(chat_b)
    assert (
        state.current_message_id == node_a.id
    ), "active chat A pointer corrupted by a delete in background chat B"
    assert (
        chat_b.current_message_id == parent_b.id
    ), "background chat B should repoint to the deleted node's parent"


# --- TF-05: a deactivated / nonexistent parent_id must not be grafted onto ----

def test_parent_id_pointing_at_deactivated_node_falls_back(client, db_session):
    # TF-05: a client-supplied parent_id for a deleted (deactivated) node must
    # not become the new turn's parent -- that would splice the reply onto a
    # dead branch. It falls back to the chat's own current pointer.
    char = Character(id=760, name="TF5", description="d")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=760)
    db_session.add(state)
    db_session.commit()
    chat = Chat(character_id=760, title="c")
    db_session.add(chat)
    db_session.commit()
    state.active_chat_id = chat.id

    active_node = MessageNode(
        character_id=760, chat_id=chat.id, role="assistant", content="alive"
    )
    dead_node = MessageNode(
        character_id=760,
        chat_id=chat.id,
        role="assistant",
        content="deleted",
        is_active=False,
    )
    db_session.add_all([active_node, dead_node])
    db_session.commit()
    state.current_message_id = active_node.id
    db_session.commit()

    async def fake_build_prompt(user_message, character, state_dict, **kwargs):
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
            json={
                "character_id": 760,
                "chat_id": chat.id,
                "message": "hi",
                "parent_id": dead_node.id,
            },
        )
    assert resp.status_code == 200
    new_user = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 760, MessageNode.content == "hi")
        .first()
    )
    assert new_user is not None
    assert (
        new_user.parent_id != dead_node.id
    ), "new turn was grafted onto a deactivated (deleted) node"
    assert new_user.parent_id == active_node.id, "should fall back to the live pointer"


# --- TF-03: streamed reply must survive a StaleDataError on persist -----------

def test_persist_assistant_reply_retries_on_stale_data():
    # TF-03: a concurrent stat PUT advances AgentState.version, so the stream's
    # persist commit raises StaleDataError. It must re-query fresh state and
    # retry rather than drop the streamed reply on the floor.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    try:
        user = User.get_or_create_active(db)
        char = Character(name="TF3", description="d")
        db.add(char)
        db.commit()
        state = AgentState(character_id=char.id)
        db.add(state)
        db.commit()
        chat = Chat(character_id=char.id, title="C")
        db.add(chat)
        db.commit()
        state.active_chat_id = chat.id
        parent = MessageNode(
            character_id=char.id, chat_id=chat.id, role="user", content="hi"
        )
        db.add(parent)
        db.commit()

        ctx = ChatTurnContext(
            user=user,
            character=char,
            state=state,
            prompt="",
            config=LLMConfig(),
            preset_dict=None,
            effective_parent_id=parent.id,
            user_message_content="hi",
            force_reflect=False,
            chat_id=chat.id,
        )

        real_commit = db.commit
        calls = {"n": 0}

        def flaky_commit():
            calls["n"] += 1
            if calls["n"] == 1:
                raise StaleDataError("simulated concurrent update")
            return real_commit()

        with patch.object(db, "commit", side_effect=flaky_commit):
            msg = _persist_assistant_reply(db, state, ctx, "streamed reply", "rid-1")

        assert msg.id is not None
        assert calls["n"] == 2, "persist should retry exactly once after StaleData"
        fresh = db.query(AgentState).filter(AgentState.id == state.id).first()
        assert fresh.current_message_id == msg.id
        assert (
            db.query(MessageNode).filter(MessageNode.content == "streamed reply").count()
            == 1
        ), "reply must be persisted exactly once (not lost, not duplicated)"
    finally:
        db.close()
        engine.dispose()
