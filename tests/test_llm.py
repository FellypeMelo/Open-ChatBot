import pytest
import httpx
from app.core.llm import LlamaClient

@pytest.mark.asyncio
async def test_llm_completion_connection_error():
    client = LlamaClient()
    client.url = "http://localhost:9999"  # Port that is likely closed
    # We expect a connection error because no server is running on this port
    with pytest.raises((httpx.ConnectError, httpx.ConnectTimeout)):
        await client.complete("Say hi")
