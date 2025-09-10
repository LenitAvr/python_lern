# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@db:5432/gamedb"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
