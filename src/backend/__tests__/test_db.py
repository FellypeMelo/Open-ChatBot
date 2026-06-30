import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.db.database import Base, init_db, vacuum_db, get_db
from src.backend.db.models import AgentState, Character


def test_create_agent_state():
    # Setup in-memory DB for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create character first
    char = Character(name="TestAgent", description="Test")
    db.add(char)
    db.commit()

    agent = AgentState(
        character_id=char.id,
        mood="Happy",
        location="Home",
        clothes="Casual",
        stats={"energy": 100},
    )
    db.add(agent)
    db.commit()

    saved_agent = db.query(AgentState).first()
    assert saved_agent.character.name == "TestAgent"
    assert saved_agent.stats["energy"] == 100
    db.close()


def test_database_init_and_vacuum():
    # Test init_db and vacuum_db runs without errors
    with patch("src.backend.db.database.engine") as mock_engine:
        # Mock engine.connect() for vacuum success
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        init_db()
        vacuum_db()

        # Test vacuum_db exception pathway
        mock_engine.connect.side_effect = Exception("DB Lock")
        vacuum_db()  # Should catch Exception and pass silently


def test_database_get_db_generator():
    # Test get_db generator yields a session and closes it
    mock_session = MagicMock()
    with patch("src.backend.db.database.SessionLocal", return_value=mock_session):
        db_generator = get_db()
        session = next(db_generator)
        assert session == mock_session

        # Clean up / finalize generator
        try:
            next(db_generator)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()
