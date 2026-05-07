import pytest
from app.core.vector_store import VectorStore
from unittest.mock import AsyncMock
import shutil
import os

@pytest.mark.asyncio
async def test_vector_store_add_and_query():
    # Clean up test dir if exists
    test_path = "./test_chroma"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
        
    # Mock the LLM client for embeddings
    mock_llm = AsyncMock()
    mock_llm.embed.return_value = [0.1] * 128 # Dummy vector
    
    store = VectorStore(llm_client=mock_llm, path=test_path)
    await store.add_memory("The user likes pizza.", metadata={"type": "preference"})
    
    results = await store.query_memory("What does the user like?", n_results=1)
    
    assert len(results["documents"]) > 0
    assert "pizza" in results["documents"][0][0]
    
    # Cleanup
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
