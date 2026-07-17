from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Host the local llama-server binds to. The per-server PORT is owned by the
    # runner config (models_config.json); this is the single source for the host
    # so it isn't re-hardcoded as a "127.0.0.1" literal across modules.
    LLAMA_HOST: str = "127.0.0.1"
    LLAMA_SERVER_URL: str = "http://127.0.0.1:8080"
    # Embeddings are served by the same consolidated llama-server on 8080 (the
    # runner migrates the old separate :8081 server onto the inference port).
    EMBEDDING_SERVER_URL: str = "http://127.0.0.1:8080"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    # Vector-memory store location. Redirected to an isolated dir under tests
    # so E2E/unit runs can never write mock memories into the real store
    # (the exact bug that poisoned real chats with test "Baile/Ballroom" data).
    CHROMA_PATH: str = "./chroma_db"
    MODEL_PATH: str = "models/model.gguf"
    DEBUG_LATENCY: bool = False
    E2E_TESTING: bool = False
    # Single source of truth for "this is a unit-test run", detected once in
    # __init__ so modules reference settings.TESTING instead of each independently
    # sniffing sys.modules for "pytest".
    TESTING: bool = False

    # Minimum cosine similarity (turbovec returns raw cosine in [-1, 1]) a RAG
    # memory must reach to be injected into the prompt. Without this, an
    # unrelated message ("hello") pulls the top-k memories regardless of
    # distance, poisoning the context with stale/hallucinated content. Tunable.
    MEMORY_RELEVANCE_THRESHOLD: float = 0.5

    # Minimum fraction of the usable token budget reserved for conversation
    # history. Without a floor, fixed layer allocations (~1560 tok) exceed the
    # usable budget on small/quantized contexts and history_budget silently
    # collapses to 0 -- the character loses all turn-to-turn recall. See
    # ContextBudgetCalculator.get_budget.
    MIN_HISTORY_BUDGET_RATIO: float = 0.25

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import sys

        self.TESTING = "pytest" in sys.modules

        if self.E2E_TESTING:
            self.DATABASE_URL = "sqlite:///./e2e_test.db"
            self.CHROMA_PATH = "./e2e_chroma_db"
        elif self.TESTING:
            # Isolate the shared vector-store singleton (core/deps.py) so unit
            # tests never read from or write to the real ./chroma_db.
            self.CHROMA_PATH = "./test_chroma_db"

    # LLM Settings for 1-4B Models
    CONTEXT_SIZE: int = 16384
    RESPONSE_SLOT: int = 1024
    TOKEN_PADDING: int = 128

    # How often (in turns) the background consciousness layer reflects+evolves.
    # Single source for what used to be a bare `20` at ~5 sites.
    REFLECTION_INTERVAL: int = 20

    # LLM HTTP timeouts (seconds). Centralized so they aren't scattered floats.
    LLM_TIMEOUT: float = 120.0
    LLM_STREAM_TIMEOUT: float = 300.0
    HEALTH_CHECK_TIMEOUT: float = 5.0

    N_PREDICT: int = 3072
    REPEAT_PENALTY: float = 1.12
    REPEAT_LAST_N: int = 512
    TEMPERATURE: float = 0.92
    TOP_P: float = 0.95
    MIN_P: float = 0.05
    TOP_K: int = 40
    SMOOTHING_FACTOR: float = 1.5
    DRY_MULTIPLIER: float = 0.0
    DRY_BASE: float = 1.75
    DRY_RANGE: int = 2048
    XTC_THRESHOLD: float = 0.0
    XTC_PROBABILITY: float = 0.0

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
