import httpx
import logging
import time
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

class LlamaClient:
    def __init__(self):
        self.url = settings.LLAMA_SERVER_URL
        self.embedding_url = settings.EMBEDDING_SERVER_URL
        # Increase timeout to 120s for slow embedding/inference servers
        self.client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        await self.client.aclose()

    async def complete(self, prompt: str, grammar: str = None):
        payload = {
            "prompt": prompt,
            "n_predict": settings.N_PREDICT,
            "temperature": 0.92,
            "top_p": 0.95,
            "top_k": 40,
            "repeat_penalty": 1.08,
            "frequency_penalty": 0.15,
            "min_p": 0.05,
            "stop": ["\n# ", "\n---", "\n\n\n"],
        }
        if grammar:
            payload["grammar"] = grammar
        
        t0 = time.perf_counter()
        try:
            logger.info(f"LLM REQ: prompt_len={len(prompt)}")
            response = await self.client.post(f"{self.url}/completion", json=payload)
            response.raise_for_status()
            dur = time.perf_counter() - t0
            res_data = response.json()
            gen_len = len(res_data.get("content", ""))
            logger.info(f"LLM RES: dur={dur:.3f}s, gen_len={gen_len}")
            return res_data
        except httpx.ReadTimeout:
            logger.error(f"Inference timed out after {time.perf_counter() - t0:.1f}s")
            raise HTTPException(status_code=504, detail="AI Inference Timeout")
        except Exception as e:
            logger.exception(f"Error during completion: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def embed(self, text: str):
        try:
            t0 = time.perf_counter()
            logger.info(f"Generating embedding for text: {text[:50]}...")
            response = await self.client.post(
                f"{self.embedding_url}/embedding", 
                json={"content": text},
                timeout=60.0 # Specific timeout for embedding
            )
            dur = time.perf_counter() - t0
            
            if response.status_code != 200:
                logger.error(f"Embedding server returned error {response.status_code} after {dur:.3f}s: {response.text}")
                return None
            
            logger.info(f"Embedding success: dur={dur:.3f}s")
            data = response.json()
            
            # Handle different llama-server versions
            if isinstance(data, list) and len(data) > 0:
                # Check for "embedding" key in the first element
                emb = data[0].get("embedding") if isinstance(data[0], dict) else None
                if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
                    return emb[0]
                return emb
            
            if isinstance(data, dict):
                return data.get("embedding")
                
            return None
        except (httpx.ReadTimeout, httpx.ConnectError):
            logger.warning("Embedding request failed or timed out. Memory features might be degraded.")
            return None
        except Exception as e:
            logger.error(f"Non-critical embedding error: {e}")
            return None

    async def health_check(self):
        """Checks if both inference and embedding servers are reachable."""
        results = {"inference": False, "embedding": False}
        
        # Check Inference Server
        try:
            response = await self.client.get(f"{self.url}/health", timeout=5.0)
            if response.status_code == 200:
                results["inference"] = True
        except Exception:
            pass
            
        # Check Embedding Server
        try:
            response = await self.client.get(f"{self.embedding_url}/health", timeout=5.0)
            if response.status_code == 200:
                results["embedding"] = True
        except Exception:
            pass
            
        return results
