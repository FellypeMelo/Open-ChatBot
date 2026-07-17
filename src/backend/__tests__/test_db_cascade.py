"""FK cascade / SET NULL regression tests.

These build an isolated in-memory engine with SQLite FK enforcement ON (matching
production's connect listener) so the ondelete rules declared on the models are
actually exercised: ownership rows cascade away with their character, while
pointer FKs null out instead of deleting their holder.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from src.backend.db.database import Base
import src.backend.db.models as m


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
