import httpx
import logging
import time
from fastapi import HTTPException
from src.backend.core.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Deterministic chunks streamed back in E2E mode (no model server running).
_E2E_STREAM_CHUNKS = [
    "Mock ",
    "E2E ",
    "stream response ",
    "**enters the Ballroom** ",
    "**changes into a Tuxedo**",
]


def _pick(preset: dict, key: str, default):
    """Read a sampler value from the preset, falling back to the default."""
    return preset.get(key, default) if preset else default


class LlamaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.LLM_TIMEOUT)
        self._url = None
        self._embedding_url = None
        # Instance-level (not class-level): each client wraps its own
        # httpx.AsyncClient, so a cache shared across instances could hand
        # one instance's requests to another instance's (possibly closed)
        # transport.
        self._chat_llm_cache: dict[tuple, ChatOpenAI] = {}
        self._embeddings_cache: dict[tuple, OpenAIEmbeddings] = {}

    @staticmethod
    def _build_extra_body(preset: dict = None, grammar: str = None) -> dict:
        """llama.cpp-specific sampler params, from the preset (if any) else
        settings defaults. Shared by complete() and complete_stream()."""
        extra_body = {
            "repeat_penalty": _pick(preset, "repeat_penalty", settings.REPEAT_PENALTY),
            "repeat_last_n": settings.REPEAT_LAST_N,
            "min_p": _pick(preset, "min_p", settings.MIN_P),
            "top_k": _pick(preset, "top_k", settings.TOP_K),
            "smoothing_factor": settings.SMOOTHING_FACTOR,
            "dry_multiplier": _pick(preset, "dry_multiplier", settings.DRY_MULTIPLIER),
            "dry_base": _pick(preset, "dry_base", settings.DRY_BASE),
            "dry_range": _pick(preset, "dry_range", settings.DRY_RANGE),
            "xtc_threshold": _pick(preset, "xtc_threshold", settings.XTC_THRESHOLD),
            "xtc_probability": _pick(
                preset, "xtc_probability", settings.XTC_PROBABILITY
            ),
        }
        if grammar:
            extra_body["grammar"] = grammar
        return extra_body

    def _get_chat_llm(
        self,
        base_url: str,
        model_name: str,
        timeout: float,
    ) -> ChatOpenAI:
        """Return a cached ChatOpenAI client for (base_url, model_name, timeout),
        constructing one on first use. These are the only values that affect
        client CONSTRUCTION. Per-call sampler settings (temperature, top_p,
        extra_body/grammar) are NOT baked in here -- they vary by preset/grammar
        on every call, so complete()/complete_stream() pass them fresh as
        ainvoke()/astream() kwargs instead, which override the (unset) instance
        defaults per-request without needing a new client."""
        key = (base_url, model_name, timeout)
        cached = self._chat_llm_cache.get(key)
        if cached is not None:
            return cached
        llm = ChatOpenAI(
            base_url=base_url,
            openai_api_key="sk-anything",
            model_name=model_name,
            max_tokens=settings.N_PREDICT,
            timeout=timeout,
            http_async_client=self.client,
        )
        self._chat_llm_cache[key] = llm
        return llm

    def _get_embeddings_client(
        self, base_url: str, model_name: str
    ) -> OpenAIEmbeddings:
        """Return a cached OpenAIEmbeddings client for (base_url, model_name)."""
        key = (base_url, model_name)
        cached = self._embeddings_cache.get(key)
        if cached is not None:
            return cached
        embeddings = OpenAIEmbeddings(
            openai_api_base=base_url,
            openai_api_key="sk-anything",
            model=model_name,
            check_embedding_ctx_length=False,
            http_async_client=self.client,
        )
        self._embeddings_cache[key] = embeddings
        return embeddings

    @property
    def url(self) -> str:
        if self._url is not None:
            return self._url
        from src.backend.core.engine.runner import runner

        return f"http://{settings.LLAMA_HOST}:{runner.config['inference']['port']}"

    @url.setter
    def url(self, value: str):
        self._url = value

    @property
    def embedding_url(self) -> str:
        if self._embedding_url is not None:
            return self._embedding_url
        from src.backend.core.engine.runner import runner

        return f"http://{settings.LLAMA_HOST}:{runner.config['embedding']['port']}"

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
        llm = self._get_chat_llm(base_url, model_name, settings.LLM_TIMEOUT)

        message = HumanMessage(content=prompt)
        t0 = time.perf_counter()
        try:
            logger.info(
                f"LLM REQ (LangChain): prompt_len={len(prompt)} target={base_url}"
            )
            response = await llm.ainvoke(
                [message],
                temperature=_pick(preset, "temperature", settings.TEMPERATURE),
                top_p=_pick(preset, "top_p", settings.TOP_P),
                extra_body=self._build_extra_body(preset, grammar),
            )
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
            for chunk in _E2E_STREAM_CHUNKS:
                yield chunk
            return

        base_url = (url or self.url) + "/v1"
        model_name = model or settings.MODEL_PATH
        llm = self._get_chat_llm(base_url, model_name, settings.LLM_STREAM_TIMEOUT)

        message = HumanMessage(content=prompt)
        try:
            async for chunk in llm.astream(
                [message],
                temperature=_pick(preset, "temperature", settings.TEMPERATURE),
                top_p=_pick(preset, "top_p", settings.TOP_P),
                extra_body=self._build_extra_body(preset, grammar),
            ):
                yield chunk.content
        except Exception as e:
            logger.exception(f"Error during LangChain streaming completion: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def embed(self, text: str, url: str = None, model: str = None):
        if settings.TESTING or settings.E2E_TESTING:
            return [0.1] * 2560

        base_url = (url or self.embedding_url) + "/v1"
        model_name = model or settings.MODEL_PATH
        embeddings = self._get_embeddings_client(base_url, model_name)
        try:
            t0 = time.perf_counter()
            logger.info(f"Generating embedding via LangChain for: {text[:50]}...")
            emb = await embeddings.aembed_query(text)
            dur = time.perf_counter() - t0
            logger.info(f"Embedding success (LangChain): dur={dur:.3f}s")
            return emb
        except Exception as e:
            logger.exception(f"Non-critical embedding error via LangChain: {e}")
            return None

    async def health_check(self):
        """Checks if both inference and embedding servers are reachable."""
        results = {"inference": False, "embedding": False}

        # Check Inference Server
        try:
            response = await self.client.get(
                f"{self.url}/health", timeout=settings.HEALTH_CHECK_TIMEOUT
            )
            if response.status_code == 200:
                results["inference"] = True
        except Exception:
            pass

        # Check Embedding Server
        try:
            response = await self.client.get(
                f"{self.embedding_url}/health", timeout=settings.HEALTH_CHECK_TIMEOUT
            )
            if response.status_code == 200:
                results["embedding"] = True
        except Exception:
            pass

        return results
