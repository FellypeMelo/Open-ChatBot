import pytest
import json
from unittest.mock import patch, AsyncMock
from app.db.models import AgentState, Character, User

def test_chat_endpoint(client, db_session):
    # Setup: Create character, user, and state in mock DB
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    
    user = User(name="TestUser", gender="Male", is_active=True)
    db_session.add(user)
    
    db_session.commit()
    
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    with patch("app.core.bridge.VectorStore.query_memory", new_callable=AsyncMock) as mock_query, \
         patch("app.api.chat.LlamaClient.complete") as mock_complete:
        
        mock_query.return_value = {"documents": [["some memory"]]}
        
        ai_response_content = json.dumps({
            "sequence": [
                {"type": "thought", "content": "I should reply hello."},
                {"type": "speech", "content": "Hello there!"}
            ]
        })
        mock_complete.return_value = {"content": ai_response_content}
        
        response = client.post("/chat", json={"message": "hello", "character_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Hello there!"
        assert data["thought"] == "I should reply hello."
        assert len(data["sequence"]) == 2
