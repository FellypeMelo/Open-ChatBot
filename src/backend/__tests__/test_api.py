import pytest
from unittest.mock import patch, AsyncMock
from src.backend.db.models import AgentState, Character, User, MessageNode

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


def test_chat_history_endpoints(client, db_session):
    # Setup
    char = Character(id=2, name="HistoryChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    
    # 1. Empty history
    resp = client.get("/history/2")
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. Populated history
    m1 = MessageNode(character_id=2, role="user", content="hello", variant_index=0)
    db_session.add(m1)
    db_session.commit()

    resp = client.get("/history/2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "hello"


def test_clear_chat_history(client, db_session):
    char = Character(id=3, name="ClearChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    
    state = AgentState(character_id=3, location="Kitchen", stats={"energy": 80})
    db_session.add(state)
    m = MessageNode(character_id=3, role="user", content="hi")
    db_session.add(m)
    db_session.commit()
    
    # 1. Clear success
    resp = client.post("/chat/clear/3")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    
    # Verify state reset
    db_session.refresh(state)
    assert state.location == "Living Room"
    assert state.stats["energy"] == 100
    
    # 2. Clear failure (triggers rollback/500)
    with patch("sqlalchemy.orm.Session.query", side_effect=Exception("Clear failed")):
        resp = client.post("/chat/clear/3")
        assert resp.status_code == 500



def test_chat_with_action_ids(client, db_session):
    char = Character(id=4, name="ActionChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    
    state = AgentState(character_id=4, stats={"energy": 50, "hunger": 20, "relationship": {"score": 50}})
    db_session.add(state)
    db_session.commit()

    with patch("src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"content": "Thank you for the croissant!"}
        
        # Test croissant action
        resp = client.post("/chat", json={"character_id": 4, "action_id": "croissant"})
        assert resp.status_code == 200
        
        # Verify stats updated (croissant: hunger -35, energy 5, relationship_score 3)
        db_session.refresh(state)
        assert state.stats["energy"] == 55
        assert state.stats["hunger"] == 0 # min clamped at 0
        assert state.stats["relationship"]["score"] == 53


def test_chat_stream_with_action_ids(client, db_session):
    char = Character(id=5, name="StreamActionChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    
    state = AgentState(character_id=5, stats={"energy": 50, "hunger": 20, "relationship": {"score": 50}})
    db_session.add(state)
    db_session.commit()

    with patch("src.backend.core.engine.llm.LlamaClient.complete_stream") as mock_stream:
        async def mock_iter(prompt, url=None, model=None):
            yield "Thanks!"
            
        mock_stream.side_effect = mock_iter
        
        # Test tease action (tease: happiness 2, social 8, relationship_score 1)
        resp = client.post("/chat/stream", json={"character_id": 5, "action_id": "tease"})
        assert resp.status_code == 200
        
        # Consume the stream so standard post-stream handlers execute
        for _ in resp.iter_bytes():
            pass
            
        db_session.refresh(state)
        assert state.stats["relationship"]["score"] == 51


def test_chat_endpoint_exceptions(client, db_session):
    # Setup: Create character to avoid character query errors
    char = Character(id=6, name="ErrChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    
    with patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete:
        # Trigger general exception
        mock_complete.side_effect = Exception("LLM crash")
        resp = client.post("/chat", json={"message": "hello", "character_id": 6})
        assert resp.status_code == 500


@pytest.mark.asyncio
async def test_run_consciousness_layer_exception():
    # Test error fallback logging inside the consciousness layer background task
    from src.backend.api.chat import run_consciousness_layer
    with patch("src.backend.api.chat.logger") as mock_logger:
        with patch("src.backend.api.chat.vector_store.add_memory", side_effect=Exception("Chroma failure")):
            await run_consciousness_layer(None, None, None)
            mock_logger.exception.assert_called()


def test_lore_endpoints(client, db_session):
    with patch("src.backend.api.lore.vector_store.add_lore", new_callable=AsyncMock) as mock_add_lore:
        mock_add_lore.return_value = None

        # POST /lore/
        lore_payload = {"keyword": "Elves", "content": "Immortal beings.", "character_id": None, "is_global": True}
        response = client.post("/lore/", json=lore_payload)
        assert response.status_code == 200
        data = response.json()
        lore_id = data["id"]
        assert data["keyword"] == "Elves"
        assert data["content"] == "Immortal beings."
        assert data["is_global"] is True
        assert mock_add_lore.called

        # GET /lore/
        response = client.get("/lore/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(l["id"] == lore_id for l in data)

        # DELETE /lore/{id}
        response = client.delete(f"/lore/{lore_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Lore entry deleted"}

        # DELETE /lore/{id} 404
        response = client.delete(f"/lore/{lore_id}")
        assert response.status_code == 404





