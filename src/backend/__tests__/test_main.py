import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.backend.main import app, lifespan

def test_static_routes(monkeypatch):
    # Test favicon and catch-all frontend routes
    mock_file_response = MagicMock(return_value="FileResponseMock")
    monkeypatch.setattr("src.backend.main.FileResponse", mock_file_response)
    
    client = TestClient(app)
    
    # Favicon endpoint
    resp = client.get("/favicon.svg")
    assert resp.status_code == 200
    mock_file_response.assert_any_call("static/favicon.svg")
    
    # Catch-all frontend route
    resp = client.get("/some/random/route")
    assert resp.status_code == 200
    mock_file_response.assert_any_call("static/index.html")


@pytest.mark.asyncio
async def test_lifespan_testing_mode():
    # Test lifespan when is_testing is True (default under pytest)
    mock_runner = MagicMock()
    with patch("src.backend.main.runner", mock_runner):
        async with lifespan(MagicMock()):
            pass
        # Should NOT start runner, health checks or stop runner
        mock_runner.start_inference.assert_not_called()
        mock_runner.stop_all.assert_not_called()


@pytest.mark.asyncio
async def test_lifespan_non_testing_mode():
    # Simulate production mode by temporarily popping "pytest" from sys.modules
    pytest_module = sys.modules.pop("pytest", None)
    try:
        mock_runner = MagicMock()
        mock_llama = MagicMock()
        
        # Test Case 1: healthy servers
        mock_llama.health_check = AsyncMock(return_value={"inference": True, "embedding": True})
        mock_llama.close = AsyncMock()
        
        with patch("src.backend.main.runner", mock_runner):
            with patch("src.backend.main.LlamaClient", return_value=mock_llama):
                with patch("asyncio.sleep", AsyncMock()): # avoid waiting 2 seconds
                    async with lifespan(MagicMock()):
                        pass
                    
                    mock_runner.start_inference.assert_called_once()
                    mock_runner.start_embedding.assert_called_once()
                    mock_llama.health_check.assert_called_once()
                    mock_runner.stop_all.assert_called_once()
                    mock_llama.close.assert_called_once()

        # Reset
        mock_runner.reset_mock()
        mock_llama.reset_mock()

        # Test Case 2: unhealthy servers (inference failed, embedding failed)
        mock_llama.health_check = AsyncMock(return_value={"inference": False, "embedding": False})
        mock_llama.close = AsyncMock()
        with patch("src.backend.main.runner", mock_runner):
            with patch("src.backend.main.LlamaClient", return_value=mock_llama):
                with patch("asyncio.sleep", AsyncMock()):
                    async with lifespan(MagicMock()):
                        pass
                    
                    mock_runner.start_inference.assert_called_once()
                    mock_runner.start_embedding.assert_called_once()
                    mock_llama.health_check.assert_called_once()
                    mock_runner.stop_all.assert_called_once()
                    mock_llama.close.assert_called_once()
    finally:
        # Restore pytest back to sys.modules
        if pytest_module is not None:
            sys.modules["pytest"] = pytest_module
