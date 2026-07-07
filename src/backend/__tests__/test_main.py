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
    mock_init_db = MagicMock()
    mock_vacuum_db = MagicMock()
    mock_seed_presets = MagicMock()
    with (
        patch("src.backend.main.runner", mock_runner),
        patch("src.backend.main.init_db", mock_init_db),
        patch("src.backend.db.database.vacuum_db", mock_vacuum_db),
        patch("src.backend.main.seed_default_presets", mock_seed_presets),
    ):
        async with lifespan(MagicMock()):
            pass
        # Should NOT start runner, health checks or stop runner
        mock_runner.start_inference.assert_not_called()
        mock_runner.stop_all.assert_not_called()
        # Should NOT touch the real database at all -- this is the
        # test-isolation guarantee from CLAUDE.md.
        mock_init_db.assert_not_called()
        mock_vacuum_db.assert_not_called()
        mock_seed_presets.assert_not_called()


@pytest.mark.asyncio
async def test_lifespan_non_testing_mode():
    # Simulate production mode by temporarily popping "pytest" from sys.modules
    pytest_module = sys.modules.pop("pytest", None)
    try:
        mock_runner = MagicMock()
        mock_llama = MagicMock()
        mock_init_db = MagicMock()
        mock_vacuum_db = MagicMock()
        mock_seed_presets = MagicMock()

        # is_testing becomes False in this test (pytest popped above), so the
        # lifespan really would call init_db()/vacuum_db()/seed_default_presets()
        # against the real chatbot.db -- mock all three so this test can never
        # touch it.
        with (
            patch("src.backend.main.init_db", mock_init_db),
            patch("src.backend.db.database.vacuum_db", mock_vacuum_db),
            patch("src.backend.main.seed_default_presets", mock_seed_presets),
        ):
            # Test Case 1: healthy servers
            mock_llama.health_check = AsyncMock(
                return_value={"inference": True, "embedding": True}
            )
            mock_llama.close = AsyncMock()

            with patch("src.backend.main.runner", mock_runner):
                with patch("src.backend.main.LlamaClient", return_value=mock_llama):
                    with patch("asyncio.sleep", AsyncMock()):  # avoid waiting 2 seconds
                        async with lifespan(MagicMock()):
                            pass

                        mock_init_db.assert_called_once()
                        mock_vacuum_db.assert_called_once()
                        mock_runner.start_inference.assert_called_once()
                        mock_runner.start_embedding.assert_called_once()
                        mock_llama.health_check.assert_called_once()
                        mock_runner.stop_all.assert_called_once()
                        mock_llama.close.assert_called_once()

            # Reset
            mock_runner.reset_mock()
            mock_llama.reset_mock()
            mock_init_db.reset_mock()
            mock_vacuum_db.reset_mock()

            # Test Case 2: unhealthy servers (inference failed, embedding failed)
            mock_llama.health_check = AsyncMock(
                return_value={"inference": False, "embedding": False}
            )
            mock_llama.close = AsyncMock()
            with patch("src.backend.main.runner", mock_runner):
                with patch("src.backend.main.LlamaClient", return_value=mock_llama):
                    with patch("asyncio.sleep", AsyncMock()):
                        async with lifespan(MagicMock()):
                            pass

                        mock_runner.start_inference.assert_called_once()
                        mock_runner.start_embedding.assert_called_once()
                        assert mock_llama.health_check.call_count == 30
                        mock_runner.stop_all.assert_called_once()
                        mock_llama.close.assert_called_once()
    finally:
        # Restore pytest back to sys.modules
        if pytest_module is not None:
            sys.modules["pytest"] = pytest_module
