"""FK cascade / SET NULL regression tests.

These build an isolated in-memory engine with SQLite FK enforcement ON (matching
production's connect listener) so the ondelete rules declared on the models are
actually exercised: ownership rows cascade away with their character, while
pointer FKs null out instead of deleting their holder.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from src.backend.db.database import Base
import src.backend.db.models as m
import src.backend.api.chat as chatmod
import src.backend.api.characters as charmod


@pytest.fixture
def fk_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    db = TestSession()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_deleting_character_cascades_owned_rows(fk_session):
    db = fk_session
    char = m.Character(name="Cascade", description="d")
    db.add(char)
    db.commit()

    db.add(m.MessageNode(character_id=char.id, role="user", content="hi"))
    db.add(m.JournalEntry(character_id=char.id, content="j"))
    db.add(m.LorebookEntry(keyword="k", character_id=char.id))
    db.add(m.AgentState(character_id=char.id))
    db.commit()

    db.delete(char)
    db.commit()

    # Every character-owned row is gone via ON DELETE CASCADE.
    assert db.query(m.MessageNode).count() == 0
    assert db.query(m.JournalEntry).count() == 0
    assert db.query(m.LorebookEntry).count() == 0
    assert db.query(m.AgentState).count() == 0


def test_deleting_pointed_at_message_nulls_agent_pointer_not_the_agent(fk_session):
    db = fk_session
    char = m.Character(name="Pointer", description="d")
    db.add(char)
    db.commit()

    msg = m.MessageNode(character_id=char.id, role="assistant", content="hello")
    db.add(msg)
    db.commit()

    state = m.AgentState(character_id=char.id, current_message_id=msg.id)
    db.add(state)
    db.commit()
    state_id = state.id

    # Delete only the message the agent points at (not via the character).
    db.query(m.MessageNode).filter(m.MessageNode.id == msg.id).delete()
    db.commit()

    refreshed = db.query(m.AgentState).filter(m.AgentState.id == state_id).first()
    # The agent survives; only its pointer is nulled (ON DELETE SET NULL).
    assert refreshed is not None
    assert refreshed.current_message_id is None


# --- API delete PATHS exercised under FK enforcement (ER-critic gap) ---------
# The endpoint delete paths (delete_chat / clear_chat_history / delete_character)
# null pointers then bulk-delete in a specific order that is only correct when
# PRAGMA foreign_keys=ON. The rest of the suite runs with FK OFF, so this order
# was validated only in production. These tests run the real paths under FK ON.


def _seed_full_scenario(db):
    """A character with a chat, a 2-node message chain, a journal, and an agent
    state whose pointers reference the chat + a message (all FK-valid, inserted
    parents-before-children so it survives FK enforcement)."""
    char = m.Character(name="Full", description="d")
    db.add(char)
    db.commit()
    chat = m.Chat(character_id=char.id, title="C")
    db.add(chat)
    db.commit()
    root = m.MessageNode(
        character_id=char.id, chat_id=chat.id, role="assistant", content="hi"
    )
    db.add(root)
    db.commit()
    child = m.MessageNode(
        character_id=char.id,
        chat_id=chat.id,
        role="user",
        content="hey",
        parent_id=root.id,
    )
    db.add(child)
    db.commit()
    db.add(m.JournalEntry(character_id=char.id, chat_id=chat.id, content="j"))
    state = m.AgentState(character_id=char.id)
    db.add(state)
    db.commit()
    state.active_chat_id = chat.id
    state.current_message_id = child.id
    chat.current_message_id = child.id
    db.commit()
    return char, chat, state, root, child


def test_delete_chat_path_is_fk_safe(fk_session):
    db = fk_session
    char, chat, state, root, child = _seed_full_scenario(db)

    fake_vs = MagicMock()
    fake_vs.clear_chat_memories = AsyncMock(return_value=0)
    with patch.object(chatmod, "vector_store", fake_vs):
        # Must complete without an IntegrityError under FK enforcement.
        asyncio.run(chatmod.delete_chat(chat.id, db=db))

    assert db.query(m.Chat).filter(m.Chat.id == chat.id).first() is None
    assert db.query(m.MessageNode).filter(m.MessageNode.chat_id == chat.id).count() == 0
    assert (
        db.query(m.JournalEntry).filter(m.JournalEntry.chat_id == chat.id).count() == 0
    )
    # The agent state survives; pointers into the deleted chat are cleared.
    db.refresh(state)
    assert state.current_message_id is None
    assert state.active_chat_id is None


def test_clear_chat_history_path_is_fk_safe(fk_session):
    db = fk_session
    char, chat, state, root, child = _seed_full_scenario(db)

    fake_vs = MagicMock()
    fake_vs.clear_character_memories = AsyncMock(return_value=0)
    with patch.object(chatmod, "vector_store", fake_vs):
        # Must complete without an IntegrityError under FK enforcement, both for
        # the bulk delete AND the subsequent greeting re-seed.
        asyncio.run(chatmod.clear_chat_history(char.id, db=db))

    # The old scenario's messages/journals are gone; this character has no
    # first_mes, so the re-seed creates a fresh chat but no greeting message.
    assert (
        db.query(m.MessageNode).filter(m.MessageNode.character_id == char.id).count()
        == 0
    )
    assert (
        db.query(m.JournalEntry).filter(m.JournalEntry.character_id == char.id).count()
        == 0
    )
    # Clear now re-seeds one fresh chat and points the live state at it (a
    # cleared character is never left session-less).
    assert db.query(m.Chat).filter(m.Chat.character_id == char.id).count() == 1
    db.refresh(state)
    assert state.current_message_id is None  # no first_mes -> no greeting node
    assert state.active_chat_id is not None


def test_delete_character_path_is_fk_safe(fk_session):
    db = fk_session
    char, chat, state, root, child = _seed_full_scenario(db)
    db.add(m.LorebookEntry(keyword="k", character_id=char.id))
    db.commit()

    fake_vs = MagicMock()
    fake_vs.clear_character_memories = AsyncMock(return_value=0)
    with patch.object(charmod, "vector_store", fake_vs):
        asyncio.run(charmod.delete_character(char.id, db=db))

    assert db.query(m.Character).filter(m.Character.id == char.id).first() is None
    assert (
        db.query(m.AgentState).filter(m.AgentState.character_id == char.id).first()
        is None
    )
    assert (
        db.query(m.MessageNode).filter(m.MessageNode.character_id == char.id).count()
        == 0
    )
    assert (
        db.query(m.JournalEntry).filter(m.JournalEntry.character_id == char.id).count()
        == 0
    )
    assert (
        db.query(m.LorebookEntry)
        .filter(m.LorebookEntry.character_id == char.id)
        .count()
        == 0
    )
    fake_vs.clear_character_memories.assert_awaited_once_with(char.id)
