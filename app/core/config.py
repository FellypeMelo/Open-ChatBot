from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLAMA_SERVER_URL: str = "http://localhost:8080"
    EMBEDDING_SERVER_URL: str = "http://localhost:8080"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    MODEL_PATH: str = "models/model.gguf"

    class Config:
        env_file = ".env"

settings = Settings()
