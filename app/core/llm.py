import httpx
from app.core.config import settings

class LlamaClient:
    def __init__(self):
        self.url = settings.LLAMA_SERVER_URL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.client.aclose()

    async def complete(self, prompt: str, grammar: str = None):
        payload = {"prompt": prompt, "n_predict": 128}
        if grammar:
            payload["grammar"] = grammar
        response = await self.client.post(f"{self.url}/completion", json=payload)
        response.raise_for_status()
        return response.json()

    async def embed(self, text: str):
        response = await self.client.post(f"{self.url}/embedding", json={"content": text})
        response.raise_for_status()
        return response.json()["embedding"]
