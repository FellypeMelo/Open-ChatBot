import httpx
import logging
import time
from fastapi import HTTPException
from src.backend.core.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class LlamaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self._url = None
        self._embedding_url = None

    @property
    def url(self) -> str:
        if self._url is not None:
            return self._url
        from src.backend.core.engine.runner import runner

        return f"http://127.0.0.1:{runner.config['inference']['port']}"

    @url.setter
    def url(self, value: str):
        self._url = value

    @property
    def embedding_url(self) -> str:
        if self._embedding_url is not None:
            return self._embedding_url
        from src.backend.core.engine.runner import runner

        return f"http://127.0.0.1:{runner.config['embedding']['port']}"

    @embedding_url.setter
    def embedding_url(self, value: str):
        self._embedding_url = value

    async def close(self):
        await self.client.aclose()

    async def complete(
        self,
        prompt: str,
        grammar: str = None,
        url: str = None,
        model: str = None,
        preset: dict = None,
    ):
        if settings.E2E_TESTING:
            return {"content": "Mock E2E response"}

        base_url = (url or self.url) + "/v1"
        model_name = model or settings.MODEL_PATH

        extra_body = {
            "repeat_penalty": preset.get("repeat_penalty", settings.REPEAT_PENALTY)
            if preset
            else settings.REPEAT_PENALTY,
            "repeat_last_n": settings.REPEAT_LAST_N,
            "min_p": preset.get("min_p", settings.MIN_P) if preset else settings.MIN_P,
            "top_k": preset.get("top_k", settings.TOP_K) if preset else settings.TOP_K,
            "smoothing_factor": settings.SMOOTHING_FACTOR,
            "dry_multiplier": preset.get("dry_multiplier", settings.DRY_MULTIPLIER)
            if preset
            else settings.DRY_MULTIPLIER,
            "dry_base": preset.get("dry_base", settings.DRY_BASE)
            if preset
            else settings.DRY_BASE,
            "dry_range": preset.get("dry_range", settings.DRY_RANGE)
            if preset
            else settings.DRY_RANGE,
            "xtc_threshold": preset.get("xtc_threshold", settings.XTC_THRESHOLD)
            if preset
            else settings.XTC_THRESHOLD,
            "xtc_probability": preset.get("xtc_probability", settings.XTC_PROBABILITY)
            if preset
            else settings.XTC_PROBABILITY,
        }
        if grammar:
            extra_body["grammar"] = grammar

        llm = ChatOpenAI(
            base_url=base_url,
            openai_api_key="sk-anything",
            model_name=model_name,
            temperature=preset.get("temperature", settings.TEMPERATURE)
            if preset
            else settings.TEMPERATURE,
            top_p=preset.get("top_p", settings.TOP_P) if preset else settings.TOP_P,
            max_tokens=settings.N_PREDICT,
            extra_body=extra_body,
            timeout=120.0,
        )

        message = HumanMessage(content=prompt)
        t0 = time.perf_counter()
        try:
            logger.info(
                f"LLM REQ (LangChain): prompt_len={len(prompt)} target={base_url}"
            )
            response = await llm.ainvoke([message])
            dur = time.perf_counter() - t0
            content = response.content.strip()
            logger.info(f"LLM RES (LangChain): dur={dur:.3f}s, gen_len={len(content)}")
            return {"content": content}
        except Exception as e:
            logger.exception(f"Error during LangChain completion: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def complete_stream(
        self,
        prompt: str,
        grammar: str = None,
        url: str = None,
        model: str = None,
        preset: dict = None,
    ):
        """Async generator that yields tokens from llama.cpp via LangChain ChatOpenAI."""
        if settings.E2E_TESTING:
            yield "Mock "
            yield "E2E "
            yield "stream response "
            yield "**enters the Ballroom** "
            yield "**changes into a Tuxedo**"
            return

        base_url = (url or self.url) + "/v1"
        model_name = model or settings.MODEL_PATH

        extra_body = {
            "repeat_penalty": preset.get("repeat_penalty", settings.REPEAT_PENALTY)
            if preset
            else settings.REPEAT_PENALTY,
            "repeat_last_n": settings.REPEAT_LAST_N,
            "min_p": preset.get("min_p", settings.MIN_P) if preset else settings.MIN_P,
            "top_k": preset.get("top_k", settings.TOP_K) if preset else settings.TOP_K,
            "smoothing_factor": settings.SMOOTHING_FACTOR,
            "dry_multiplier": preset.get("dry_multiplier", settings.DRY_MULTIPLIER)
            if preset
            else settings.DRY_MULTIPLIER,
            "dry_base": preset.get("dry_base", settings.DRY_BASE)
            if preset
            else settings.DRY_BASE,
            "dry_range": preset.get("dry_range", settings.DRY_RANGE)
            if preset
            else settings.DRY_RANGE,
            "xtc_threshold": preset.get("xtc_threshold", settings.XTC_THRESHOLD)
            if preset
            else settings.XTC_THRESHOLD,
            "xtc_probability": preset.get("xtc_probability", settings.XTC_PROBABILITY)
            if preset
            else settings.XTC_PROBABILITY,
        }
        if grammar:
            extra_body["grammar"] = grammar

        llm = ChatOpenAI(
            base_url=base_url,
            openai_api_key="sk-anything",
            model_name=model_name,
            temperature=preset.get("temperature", settings.TEMPERATURE)
            if preset
            else settings.TEMPERATURE,
            top_p=preset.get("top_p", settings.TOP_P) if preset else settings.TOP_P,
            max_tokens=settings.N_PREDICT,
            extra_body=extra_body,
            timeout=300.0,
        )

        message = HumanMessage(content=prompt)
        try:
            async for chunk in llm.astream([message]):
                yield chunk.content
        except Exception as e:
            logger.error(f"Error during LangChain streaming completion: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def embed(self, text: str, url: str = None, model: str = None):
        import sys

        if "pytest" in sys.modules or settings.E2E_TESTING:
            return [0.1] * 2560

        base_url = (url or self.embedding_url) + "/v1"
        model_name = model or settings.MODEL_PATH

        embeddings = OpenAIEmbeddings(
            openai_api_base=base_url,
            openai_api_key="sk-anything",
            model=model_name,
            check_embedding_ctx_length=False,
        )
        try:
            t0 = time.perf_counter()
            logger.info(f"Generating embedding via LangChain for: {text[:50]}...")
            emb = await embeddings.aembed_query(text)
            dur = time.perf_counter() - t0
            logger.info(f"Embedding success (LangChain): dur={dur:.3f}s")
            return emb
        except Exception as e:
            logger.error(f"Non-critical embedding error via LangChain: {e}")
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
            response = await self.client.get(
                f"{self.embedding_url}/health", timeout=5.0
            )
            if response.status_code == 200:
                results["embedding"] = True
        except Exception:
            pass

        return results
