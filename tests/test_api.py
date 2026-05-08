import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.database import Base, get_db
from app.db.models import AgentState, Character

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

def test_chat_endpoint(client, db_session):
    # Setup: Create character and state in mock DB
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    db_session.commit()
    
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    with patch("app.api.chat.VectorStore.query_memory") as mock_query, \
         patch("app.api.chat.LlamaClient.complete") as mock_complete:
        
        mock_query.return_value = {"documents": [["some memory"]]}
        
        ai_response_content = json.dumps({
            "thought": "I should reply hello.",
            "actions": [],
            "message": "Hello there!"
        })
        mock_complete.return_value = {"content": ai_response_content}
        
        response = client.post("/chat", json={"message": "hello", "character_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Hello there!"
        assert data["thought"] == "I should reply hello."
