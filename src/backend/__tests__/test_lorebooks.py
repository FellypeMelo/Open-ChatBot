import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import MagicMock, AsyncMock
from src.backend.core.orchestration.bridge import Brain
from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import Character, User


@pytest.mark.asyncio
async def test_lorebook_integration():
    # Setup temporary directory for ChromaDB
    tmp_dir = tempfile.mkdtemp()

    try:
        # Mock LLM
        llm_mock = MagicMock()
        llm_mock.embed = AsyncMock(return_value=[0.1] * 1536)

        # Real VectorStore with temp directory
        vs = VectorStore(llm_client=llm_mock, path=tmp_dir)

        from unittest.mock import patch

        with patch(
            "src.backend.core.context.lorebook_scanner.LorebookScanner"
        ) as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner.scan_and_extract.return_value = [
                "The Sword of Destiny is a legendary blade forged in the fires of Mount Doom."
            ]
            mock_scanner_class.return_value = mock_scanner

            brain = Brain(vector_store=vs, llm_client=llm_mock)

            char = Character(id=1, name="Gemi", description="A playful entity.")
            user = User(name="Alex", gender="Non-binary")
            state = {"location": "Workshop", "mood": "Happy", "stats": {"energy": 100}}

            # Message containing "sword" (keyword trigger)
            user_msg = "I draw my sword."

            # Pass a dummy db so it triggers the scan
            prompt = await brain.build_prompt(
                user_msg, char, state, user=user, db=MagicMock()
            )

            # Assertions
            assert "Lore:" in prompt
            assert "Sword of Destiny" in prompt
            assert "legendary blade" in prompt

    finally:
        # Cleanup
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(test_lorebook_integration())
