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

def test_update_character_state(client, db_session):
    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    update_payload = {
        "location": "Kitchen",
        "stats": {
            "energy": 90,
            "hunger": 10,
            "relationship_score": 75
        }
    }
    response = client.put("/characters/1/state", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["location"] == "Kitchen"
    assert data["state"]["stats"]["energy"] == 90
    assert data["state"]["stats"]["hunger"] == 10
    assert data["state"]["stats"]["relationship"]["score"] == 75

def test_user_endpoints(client, db_session):
    # GET /me (creates default)
    response = client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "User"
    assert data["gender"] == "Male"

    # POST /me (updates user)
    update_payload = {"name": "Elara", "gender": "Female"}
    response = client.post("/users/me", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Elara"
    assert data["gender"] == "Female"

def test_tag_endpoints(client, db_session):
    # POST /tags/
    tag_payload = {"label": "Sarcastic", "instruction": "Make sarcastic comments."}
    response = client.post("/tags/", json=tag_payload)
    assert response.status_code == 200
    data = response.json()
    tag_id = data["id"]
    assert data["label"] == "Sarcastic"
    assert data["instruction"] == "Make sarcastic comments."

    # GET /tags/
    response = client.get("/tags/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(t["id"] == tag_id for t in data)

    # PUT /tags/{id}
    update_payload = {"label": "Sarcastic!", "instruction": "Be very sarcastic."}
    response = client.put(f"/tags/{tag_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Sarcastic!"
    assert data["instruction"] == "Be very sarcastic."

    # DELETE /tags/{id}
    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Tag deleted"}

    # DELETE /tags/{id} 404
    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 404

def test_settings_endpoints(client):
    with patch("src.backend.api.settings.runner.get_status") as mock_status, \
         patch("src.backend.api.settings.runner.save_config") as mock_save, \
         patch("src.backend.api.settings.runner.start_inference") as mock_start_inf, \
         patch("src.backend.api.settings.runner.stop_inference") as mock_stop_inf, \
         patch("src.backend.api.settings.runner.start_embedding") as mock_start_emb, \
         patch("src.backend.api.settings.runner.stop_embedding") as mock_stop_emb:
        
        mock_status.return_value = {"inference": {"running": False}, "embedding": {"running": False}}
        mock_start_inf.return_value = True
        mock_start_emb.return_value = True

        # GET /status
        response = client.get("/settings/status")
        assert response.status_code == 200
        assert response.json()["inference"]["running"] is False

        # POST /save
        cfg_payload = {
            "inference": {
                "binary_path": "llama_bin/llama-server.exe",
                "model_path": "models/qwen.gguf",
                "port": 8080,
                "threads": 4,
                "gpu_layers": -1,
                "context_size": 4096,
                "additional_args": ""
            },
            "embedding": {
                "binary_path": "llama_bin/llama-server.exe",
                "model_path": "models/qwen-emb.gguf",
                "port": 8081,
                "threads": 4,
                "gpu_layers": -1,
                "context_size": 4096,
                "additional_args": ""
            }
        }
        response = client.post("/settings/save", json=cfg_payload)
        assert response.status_code == 200
        assert mock_save.called

        # POST /start/inference
        response = client.post("/settings/start/inference")
        assert response.status_code == 200
        assert mock_start_inf.called

        # POST /stop/inference
        response = client.post("/settings/stop/inference")
        assert response.status_code == 200
        assert mock_stop_inf.called

        # POST /start/embedding
        response = client.post("/settings/start/embedding")
        assert response.status_code == 200
        assert mock_start_emb.called

        # POST /stop/embedding
        response = client.post("/settings/stop/embedding")
        assert response.status_code == 200
        assert mock_stop_emb.called

        # POST /restart-all
        response = client.post("/settings/restart-all")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

def test_settings_endpoints_failures(client):
    with patch("src.backend.api.settings.runner.get_status") as mock_status, \
         patch("src.backend.api.settings.runner.save_config") as mock_save, \
         patch("src.backend.api.settings.runner.start_inference") as mock_start_inf, \
         patch("src.backend.api.settings.runner.start_embedding") as mock_start_emb:
        
        # Test status raising exception -> 500
        mock_status.side_effect = Exception("Status error")
        response = client.get("/settings/status")
        assert response.status_code == 500

        # Test save raising exception -> 500
        mock_save.side_effect = Exception("Save error")
        cfg_payload = {
            "inference": {"binary_path": "", "model_path": "", "port": 8080, "threads": 4, "gpu_layers": -1, "additional_args": ""},
            "embedding": {"binary_path": "", "model_path": "", "port": 8080, "threads": 4, "gpu_layers": -1, "additional_args": ""}
        }
        response = client.post("/settings/save", json=cfg_payload)
        assert response.status_code == 500

        # Test start inference returns False -> 500
        mock_start_inf.return_value = False
        response = client.post("/settings/start/inference")
        assert response.status_code == 500

        # Test start embedding returns False -> 500
        mock_start_emb.return_value = False
        response = client.post("/settings/start/embedding")
        assert response.status_code == 500

def test_user_endpoints_no_user_exist(client, db_session):
    # Ensure no users exist in database
    from src.backend.db.models import User
    db_session.query(User).delete()
    db_session.commit()

    # POST /me (should create new user since none exists)
    update_payload = {"name": "Bob", "gender": "Male"}
    response = client.post("/users/me", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bob"

def test_tag_endpoints_404(client):
    # PUT /tags/99999 -> 404
    response = client.put("/tags/99999", json={"label": "Nonexistent", "instruction": ""})
    assert response.status_code == 404

    # DELETE /tags/99999 -> 404
    response = client.delete("/tags/99999")
    assert response.status_code == 404


