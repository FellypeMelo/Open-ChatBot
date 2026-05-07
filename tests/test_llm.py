import pytest
from app.core.llm import LlamaClient

@pytest.mark.asyncio
async def test_llm_completion():
    client = LlamaClient()
    # This assumes a llama-server is running on the configured port
    # We expect this to fail during 'Red' phase as LlamaClient doesn't exist yet
    response = await client.complete("Say hi")
    assert "content" in response
