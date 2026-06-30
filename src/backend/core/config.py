from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LLAMA_SERVER_URL: str = "http://127.0.0.1:8080"
    EMBEDDING_SERVER_URL: str = "http://127.0.0.1:8081"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    MODEL_PATH: str = "models/model.gguf"
    DEBUG_LATENCY: bool = False
    E2E_TESTING: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.E2E_TESTING:
            self.DATABASE_URL = "sqlite:///./e2e_test.db"

    # LLM Settings for 1-4B Models
    CONTEXT_SIZE: int = 8192
    RESPONSE_SLOT: int = 1024
    TOKEN_PADDING: int = 128

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
