import pytest
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
        
        narrative = (
            "*Gemi tilts her head, a playful smirk crossing her face.*\n\n"
            "\"Hello there! Was wondering when you'd show up.\""
        )
        mock_complete.return_value = {"content": narrative}
        
        response = client.post("/chat", json={"message": "hello", "character_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert "Hello there" in data["reply"]
        assert "stats" in data
