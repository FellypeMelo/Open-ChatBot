import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Need to import app after mocking or ensure it's available
# Since app/main.py doesn't exist yet, this will fail on import.
# That's a valid "Red" state.

def test_chat_endpoint():
    from app.main import app
    client = TestClient(app)
    
    with patch("app.api.chat.LlamaClient.complete") as mock_complete:
        mock_complete.return_value = {"content": "mocked reply"}
        
        response = client.post("/chat", json={"message": "hello"})
        
        assert response.status_code == 200
        assert response.json() == {"reply": "mocked reply"}
        mock_complete.assert_called_once()
