from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLAMA_SERVER_URL: str = "http://localhost:8080"
    EMBEDDING_SERVER_URL: str = "http://localhost:8081"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    MODEL_PATH: str = "models/model.gguf"
    DEBUG_LATENCY: bool = False
    N_PREDICT: int = 3072
    REPEAT_PENALTY: float = 1.12
    REPEAT_LAST_N: int = 512
    TEMPERATURE: float = 0.92
    TOP_P: float = 0.95
    MIN_P: float = 0.05
    TOP_K: int = 40
    SMOOTHING_FACTOR: float = 1.5

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
