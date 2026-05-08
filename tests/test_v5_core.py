import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import Character, Tag, AgentState
from app.core.bridge import Brain
from unittest.mock import AsyncMock

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_character_creation_with_tags(db):
    # 1. Create Tags
    dominant = Tag(label="Dominant", instruction="Be assertive.")
    db.add(dominant)
    db.commit()

    # 2. Create Character
    char = Character(name="Luna", description="A mysterious entity.", tags=[dominant])
    db.add(char)
    db.commit()

    # 3. Create State
    state = AgentState(character_id=char.id)
    db.add(state)
    db.commit()

    saved_char = db.query(Character).first()
    assert saved_char.name == "Luna"
    assert saved_char.tags[0].label == "Dominant"
    assert saved_char.state.character_id == saved_char.id
    assert saved_char.state.stats["energy"] == 100

@pytest.mark.asyncio
async def test_brain_v5_prompt_assembly():
    mock_vector = AsyncMock()
    mock_vector.query_memory.return_value = {"documents": [["Memory of stars"]]}
    
    brain = Brain(vector_store=mock_vector)
    
    # Mock data objects
    class MockTag:
        label = "Teasing"
        instruction = "Poke fun at the user."
    
    class MockChar:
        id = 1
        name = "Gemi"
        description = "A playful entity."
        tags = [MockTag()]
        
    state = {
        "location": "Garden",
        "mood": "Playful",
        "clothes": "Floral Dress",
        "stats": {
            "energy": 80,
            "hunger": 20,
            "happiness": 90,
            "social": 100,
            "relationship": {"score": 75, "user_sentiment": "Positive"}
        }
    }

    prompt = await brain.build_prompt("Hi!", MockChar(), state)
    
    assert "MASTER PROMPT" in prompt
    assert "Gemi" in prompt
    assert "Garden" in prompt
    assert "TEASING" in prompt
    assert "Memory of stars" in prompt
    assert "Floral Dress" in prompt
