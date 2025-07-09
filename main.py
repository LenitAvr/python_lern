from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Game, Provider
from database import get_db
from typing import Optional
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Настройка подключения к PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@db/gamedb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}

app = FastAPI()


class SearchResult(BaseModel):
    games: list[int] = []
    providers: list[int] = []


@app.get("/search/", response_model=SearchResult)
async def search(
        query: Optional[str] = Query(None, min_length=2, max_length=100),
        db: AsyncSession = Depends(get_db)
):
    result = SearchResult()

    if query:
        # Поиск игр
        games_stmt = select(Game.id).where(Game.title.ilike(f"%{query}%"))
        games_result = await db.execute(games_stmt)
        result.games = [row[0] for row in games_result]

        # Поиск провайдеров
        providers_stmt = select(Provider.id).where(Provider.name.ilike(f"%{query}%"))
        providers_result = await db.execute(providers_stmt)
        result.providers = [row[0] for row in providers_result]

    return result
