import pytest
import json
from app.api.chat import clean_json_response, ACTION_GRAMMAR
from app.api import chat as chat_module
from unittest.mock import patch

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
    assert cleaned["reply"] == "I am not JSON at all."

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


def test_action_grammar_is_valid():
    """Grammar constant must exist and define a valid JSON structure."""
    assert ACTION_GRAMMAR is not None
    assert isinstance(ACTION_GRAMMAR, str)
    assert len(ACTION_GRAMMAR) > 50
    assert "root" in ACTION_GRAMMAR
    assert "thought" in ACTION_GRAMMAR
    assert "action" in ACTION_GRAMMAR
    assert "speech" in ACTION_GRAMMAR
    assert "sequence" in ACTION_GRAMMAR


def test_grammar_constrained_output_passes_fast_path():
    """Output matching the grammar should parse directly without cleanup."""
    raw = '{"sequence": [{"type": "thought", "content": "I wonder why."}, {"type": "speech", "content": "Why?"}]}'
    result = clean_json_response(raw)
    assert result["sequence"][0]["type"] == "thought"
    assert result["sequence"][1]["content"] == "Why?"


def test_grammar_not_passed_to_llm_complete(client, db_session):
    """Grammar constraint should NOT be passed (removed for low-end model compat)."""
    from app.db.models import Character, User, AgentState
    char = Character(id=2, name="Luna", description="Test")
    db_session.add(char)
    user = User(name="Alice", gender="Female", is_active=True)
    db_session.add(user)
    state = AgentState(character_id=2)
    db_session.add(state)
    db_session.commit()

    with patch("app.api.chat.llama.complete") as mock_complete, \
         patch("app.api.chat.Brain.build_prompt") as mock_prompt:

        mock_prompt.return_value = "Prompt"
        mock_complete.return_value = {"content": '{"sequence": [{"type": "speech", "content": "Hi"}]}'}

        client.post("/chat", json={"message": "hello", "character_id": 2})

        # Verify NO grammar was passed (it should be None or absent)
        assert len(mock_complete.call_args_list) >= 1
        _args, first_kwargs = mock_complete.call_args_list[0]
        grammar = first_kwargs.get("grammar")
        assert grammar is None
