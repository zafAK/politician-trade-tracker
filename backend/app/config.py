
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore") #Read on

    database_url: str =  "sqlite:///./trades.db"

    tradesource: str = "fixture"


settings = Settings()