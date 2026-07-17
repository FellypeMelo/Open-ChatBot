"""Turn-flow / message-tree integrity tests (F5). These target concrete tree
corruption failure modes in edit/delete/persist. All isolated: no llama-server,
no real DB, no vector store (vector_store is patched to an AsyncMock).
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.backend.api.chat import (
    edit_message,
    delete_message,
    MessageEditRequest,
)
from src.backend.db.models import AgentState, Character, MessageNode, Chat


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
