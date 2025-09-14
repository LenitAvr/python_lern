from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # --- database ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    # --- redis ---
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    CACHE_TTL: int = 300

    # --- app ---
    APP_NAME: str = "SearchEnpoint"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()