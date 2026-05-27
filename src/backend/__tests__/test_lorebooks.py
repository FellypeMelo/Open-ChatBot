import pytest
import asyncio
from unittest.mock import MagicMock
from src.backend.core.orchestration.bridge import Brain
from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import Character, User

@pytest.mark.asyncio
async def test_lorebook_integration():
    # Mock LLM and VectorStore
    llm_mock = MagicMock()
    llm_mock.embed = MagicMock(side_effect=lambda x: asyncio.Future())
    llm_mock.embed.return_value.set_result([0.1] * 1536)
    
    # We need a real-ish VectorStore but with mocked collection
    vs = VectorStore(llm_client=llm_mock, path=":memory:")
    vs.lore_collection = MagicMock()
    
    # Setup lore query return value
    vs.lore_collection.query.return_value = {
        "documents": [["The Sword of Destiny is a legendary blade forged in the fires of Mount Doom."]]
    }
    
    brain = Brain(vector_store=vs, llm_client=llm_mock)
    
    char = Character(id=1, name="Gemi", description="A playful entity.")
    user = User(name="Alex", gender="Non-binary")
    state = {"location": "Workshop", "mood": "Happy", "stats": {"energy": 100}}
    
    # Message containing "sword" (keyword trigger)
    user_msg = "I draw my sword."
    
    prompt = await brain.build_prompt(user_msg, char, state, user=user)
    
    # Assertions
    assert "RELEVANT WORLD LORE:" in prompt
    assert "Sword of Destiny" in prompt
    assert "legendary blade" in prompt
    
    print("Lorebook integration verified successfully.")

if __name__ == "__main__":
    asyncio.run(test_lorebook_integration())
