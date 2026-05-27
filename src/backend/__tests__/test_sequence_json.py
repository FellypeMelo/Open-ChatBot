import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from src.backend.main import app
from src.backend.db.database import Base, get_db
from src.backend.db.models import AgentState, Character, User

# Setup in-memory DB for testing
TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)

@pytest.fixture
def db_session():
    connection = TEST_ENGINE.connect()
    transaction = connection.begin()
    db = TestSessionLocal(bind=connection)
    
    yield db
    
    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_chat_narrative_response(client, db_session):
    # Setup: Create character, user, and state in mock DB
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    
    user = User(name="TestUser", gender="Non-binary", is_active=True)
    db_session.add(user)
    
    db_session.commit()
    
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    with patch("src.backend.core.orchestration.bridge.VectorStore.query_memory") as mock_query, \
         patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete:
        
        mock_query.return_value = {"documents": [["some memory"]]}
        
        narrative = (
            "*Gemi looks up from her sketchbook, a slow smile spreading across her face.*\n\n"
            "\"Well, well... look who finally decided to say hello.\"\n\n"
            "*She sets down her pencil and leans forward, resting her chin on her hand.* "
            "Her eyes study you with an amused glint.\n\n"
            "\"I was starting to think you'd forgotten about me. Sit. Tell me everything.\""
        )
        mock_complete.return_value = {"content": narrative}
        
        response = client.post("/chat", json={"message": "hello", "character_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert "Gemi" in data["reply"]
        assert "finally decided to say hello" in data["reply"]
        assert "*Gemi looks up*" not in data["reply"]  # Only the raw content

def test_build_prompt_user_info(db_session):
    from src.backend.core.orchestration.bridge import Brain
    from src.backend.core.memory.vector_store import VectorStore
    
    mock_vector_store = MagicMock(spec=VectorStore)
    mock_vector_store.query_memory.return_value = {"documents": []}
    
    brain = Brain(vector_store=mock_vector_store)
    
    char = Character(id=1, name="Gemi", description="Test")
    user = User(name="Alice", gender="Female")
    state_data = {"stats": {"energy": 100, "hunger": 0, "happiness": 100, "social": 100}}
    
    import asyncio
    prompt = asyncio.run(brain.build_prompt("Hi", char, state_data, user=user))
    
    assert "INTERACTING WITH USER: Alice (Female)" in prompt
    assert "DYNAMIC BIOLOGICAL MODIFIERS:" in prompt
