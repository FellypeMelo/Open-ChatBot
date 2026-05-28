import pytest
from unittest.mock import patch, AsyncMock
from src.backend.db.models import AgentState, Character, User

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

    with patch("src.backend.core.orchestration.bridge.VectorStore.query_memory", new_callable=AsyncMock) as mock_query, \
         patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete:
        
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

def test_chat_with_config(client, db_session):
    # Setup
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    user = User(name="TestUser", is_active=True)
    db_session.add(user)
    db_session.commit()
    
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    with patch("src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"content": "Hello!"}
        
        config = {"base_url": "http://custom-server:1234/v1", "model_name": "custom-model"}
        response = client.post("/chat", json={
            "message": "hi", 
            "character_id": 1,
            "config": config
        })
        
        assert response.status_code == 200
        # Verify that llama.complete was called with the custom config
        args, kwargs = mock_complete.call_args
        assert kwargs["url"] == config["base_url"]
        assert kwargs["model"] == config["model_name"]

def test_chat_stream_with_config(client, db_session):
    # Setup
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    user = User(name="TestUser", is_active=True)
    db_session.add(user)
    db_session.commit()
    
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    with patch("src.backend.core.engine.llm.LlamaClient.complete_stream") as mock_stream:
        async def mock_iter(prompt, url=None, model=None):
            yield "Hello"
            yield "!"
        
        mock_stream.side_effect = mock_iter
        
        config = {"base_url": "http://stream-server:1234/v1", "model_name": "stream-model"}
        response = client.post("/chat/stream", json={
            "message": "hi", 
            "character_id": 1,
            "config": config
        })
        
        assert response.status_code == 200
        
        # Consume the response
        content = b""
        for chunk in response.iter_bytes():
            content += chunk
        
        assert b"Hello" in content
        assert b"!" in content
        
        args, kwargs = mock_stream.call_args
        assert kwargs["url"] == config["base_url"]
        assert kwargs["model"] == config["model_name"]
