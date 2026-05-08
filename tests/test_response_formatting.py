import pytest
import json
from app.api.chat import clean_json_response

def test_clean_json_robustness():
    # 1. Standard valid JSON
    raw = '{"sequence": [{"type": "speech", "content": "Hello"}]}'
    assert clean_json_response(raw)["sequence"][0]["content"] == "Hello"

    # 2. JSON wrapped in markdown
    raw = '```json\n{"sequence": [{"type": "thought", "content": "I am thinking"}]}\n```'
    assert clean_json_response(raw)["sequence"][0]["content"] == "I am thinking"

    # 3. JSON with trailing garbage
    raw = '{"sequence": [{"type": "action", "content": "Walks"}]} --- This was my response.'
    assert clean_json_response(raw)["sequence"][0]["content"] == "Walks"

    # 4. Completely invalid JSON -> Fallback
    raw = "I am not JSON at all."
    cleaned = clean_json_response(raw)
    assert cleaned["sequence"][0]["type"] == "speech"
    assert cleaned["sequence"][0]["content"] == "I am not JSON at all."

def test_sequence_block_extraction(client, db_session):
    # Integration test for sequence parsing in the endpoint
    from app.db.models import Character, User, AgentState
    char = Character(id=1, name="Luna", description="Test")
    db_session.add(char)
    user = User(name="Alice", gender="Female", is_active=True)
    db_session.add(user)
    state = AgentState(character_id=1)
    db_session.add(state)
    db_session.commit()

    from unittest.mock import patch
    with patch("app.core.bridge.Brain.build_prompt") as mock_prompt, \
         patch("app.api.chat.LlamaClient.complete") as mock_complete:
        
        mock_prompt.return_value = "Prompt"
        ai_response = {
            "sequence": [
                {"type": "thought", "content": "Thinking..."},
                {"type": "action", "content": "Smiling."},
                {"type": "speech", "content": "Hello Alice!"}
            ]
        }
        mock_complete.return_value = {"content": json.dumps(ai_response)}
        
        response = client.post("/chat", json={"message": "hi", "character_id": 1})
        assert response.status_code == 200
        data = response.json()
        
        assert data["reply"] == "Hello Alice!"
        assert data["thought"] == "Thinking..."
        assert "Smiling." in data["actions"]
        assert len(data["sequence"]) == 3
