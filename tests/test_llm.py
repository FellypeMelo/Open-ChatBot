import pytest
import httpx
from app.core.llm import LlamaClient

@pytest.mark.asyncio
async def test_llm_completion_connection_error():
    client = LlamaClient()
    # We expect a connection error because no server is running
    with pytest.raises(httpx.ConnectError):
        await client.complete("Say hi")
