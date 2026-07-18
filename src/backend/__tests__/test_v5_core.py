import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.db.database import Base
from src.backend.db.models import Character, Tag, AgentState
from src.backend.core.orchestration.bridge import Brain
from unittest.mock import MagicMock, AsyncMock

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    mock_vector = MagicMock()
    mock_vector.query_memory = AsyncMock(
        return_value={"documents": [["Memory of stars"]]}
    )
    mock_vector.query_lore = AsyncMock(return_value={})
    mock_vector.llm_client = MagicMock()

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
        "stats": {
            "energy": 80,
            "hunger": 20,
            "happiness": 90,
            "social": 100,
            "relationship": {"score": 75, "user_sentiment": "Positive"},
        },
    }

    prompt = await brain.build_prompt("Hi!", MockChar(), state)

    assert "never an AI" in prompt
    assert "Gemi" in prompt
    assert "Garden" in prompt
    assert "[Teasing]" in prompt
    assert "Memory of stars" in prompt
