from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLAMA_SERVER_URL: str = "http://localhost:8080"
    EMBEDDING_SERVER_URL: str = "http://localhost:8081"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    MODEL_PATH: str = "models/model.gguf"
    DEBUG_LATENCY: bool = False
    N_PREDICT: int = 3072

    class Config:
        env_file = ".env"

settings = Settings()
