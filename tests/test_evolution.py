import pytest
from app.core.evolution import EvolutionManager
from app.db.models import AgentState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_evolution_updates_state(db):
    # Setup agent
    agent = AgentState(name="Gemi", stats={"favorites": {"food": ["Pizza"]}})
    db.add(agent)
    db.commit()
    
    manager = EvolutionManager(db=db)
    reflection = {
        "summary": "User keeps talking about sushi.",
        "facts": ["User likes sushi now."],
        "traits": {"favorites": {"food": ["Sushi"]}}
    }
    
    manager.evolve(agent_id=agent.id, reflection=reflection)
    
    # Refresh agent from DB
    db.refresh(agent)
    # Verify list extension and content
    assert "Pizza" in agent.stats["favorites"]["food"]
    assert "Sushi" in agent.stats["favorites"]["food"]
    assert len(agent.stats["favorites"]["food"]) == 2
    
    assert agent.stats["last_reflection_summary"] == "User keeps talking about sushi."
    assert "User likes sushi now." in agent.stats["facts"]

def test_evolution_no_duplicates(db):
    agent = AgentState(name="Gemi", stats={"facts": ["Likes cats"]})
    db.add(agent)
    db.commit()
    
    manager = EvolutionManager(db=db)
    reflection = {
        "facts": ["Likes cats", "Likes dogs"]
    }
    
    manager.evolve(agent_id=agent.id, reflection=reflection)
    db.refresh(agent)
    
    assert agent.stats["facts"] == ["Likes cats", "Likes dogs"]

def test_evolution_rollback_on_error(db):
    agent = AgentState(name="Gemi", stats={"val": 10})
    db.add(agent)
    db.commit()
    
    manager = EvolutionManager(db=db)
    
    # Mock deep_merge to fail
    import unittest.mock as mock
    with mock.patch.object(EvolutionManager, '_deep_merge', side_effect=Exception("Failed")):
        with pytest.raises(Exception):
            manager.evolve(agent.id, {"traits": {"val": 20}})
            
    db.refresh(agent)
    assert agent.stats["val"] == 10
