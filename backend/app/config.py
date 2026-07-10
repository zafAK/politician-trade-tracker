from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str =  "sqlite:///./trades.db"

    tradesource: str = "fixture"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    llm_provider: str = "mock"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

settings = Settings()