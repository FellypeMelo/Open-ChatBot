import httpx
from app.core.config import settings

class LlamaClient:
    def __init__(self):
        self.url = settings.LLAMA_SERVER_URL

    async def complete(self, prompt: str, grammar: str = None):
        payload = {
            "prompt": prompt,
            "n_predict": 128,
        }
        if grammar:
            payload["grammar"] = grammar
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.url}/completion", json=payload)
            response.raise_for_status()
            return response.json()
