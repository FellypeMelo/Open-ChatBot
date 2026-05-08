import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import AgentState, Character

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
        stats={"energy": 100}
    )
    db.add(agent)
    db.commit()
    
    saved_agent = db.query(AgentState).first()
    assert saved_agent.character.name == "TestAgent"
    assert saved_agent.stats["energy"] == 100
    db.close()
