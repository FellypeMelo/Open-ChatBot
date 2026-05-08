import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import AgentState
from app.api.chat import process_ai_response

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.mark.asyncio
async def test_process_actions_move(db_session):
    # Setup agent
    agent = AgentState(
        id=1, 
        name="Gemi", 
        location="Living Room", 
        mood="Neutral",
        stats={"energy": 100}
    )
    db_session.add(agent)
    db_session.commit()
    
    ai_output = {
        "thought": "I want to go to the bedroom.",
        "actions": [{"type": "move", "location": "Bedroom"}],
        "message": "Going to bed."
    }
    
    await process_ai_response(agent.id, ai_output, db_session)
    
    # Refresh from DB
    db_session.refresh(agent)
    assert agent.location == "Bedroom"

@pytest.mark.asyncio
async def test_process_actions_set_mood(db_session):
    # Setup agent
    agent = AgentState(
        id=2, 
        name="Gemi", 
        location="Living Room", 
        mood="Neutral",
        stats={"energy": 100}
    )
    db_session.add(agent)
    db_session.commit()
    
    ai_output = {
        "thought": "I'm feeling sleepy.",
        "actions": [{"type": "set_mood", "mood": "Sleepy"}],
        "message": "Goodnight!"
    }
    
    await process_ai_response(agent.id, ai_output, db_session)
    
    # Refresh from DB
    db_session.refresh(agent)
    assert agent.mood == "Sleepy"
