import httpx
from app.core.config import settings

class LlamaClient:
    def __init__(self):
        self.url = settings.LLAMA_SERVER_URL
        self.embedding_url = settings.EMBEDDING_SERVER_URL
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
        try:
            response = await self.client.post(f"{self.embedding_url}/embedding", json={"content": text})
            response.raise_for_status()
            data = response.json()
            
            # Handle different llama-server versions
            if isinstance(data, list) and len(data) > 0:
                # Newer versions return a list of objects
                emb = data[0].get("embedding")
                if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
                    # It's a list of lists (batching)
                    return emb[0]
                return emb
            
            return data.get("embedding")
        except Exception as e:
            print(f"Embedding error: {e}")
            raise
