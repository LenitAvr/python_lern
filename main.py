import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from pydantic import BaseModel
from models import Game, Provider
from database import get_db, engine, Base

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}

class SearchResult(BaseModel):
    games: list[int] = []
    providers: list[int] = []

# Основной поисковый эндпоинт
@app.get("/search/", response_model=SearchResult)
async def search(
        query: Optional[str] = Query(None, min_length=2, max_length=100),
        db: AsyncSession = Depends(get_db)
):
    if not query:
        return SearchResult()

    try:
        # Поиск игр
        games_result = await db.execute(
            select(Game.id).where(Game.title.ilike(f"%{query}%"))
        )
        games_ids = [row[0] for row in games_result.scalars().all()]

        # Поиск провайдеров
        providers_result = await db.execute(
            select(Provider.id).where(Provider.name.ilike(f"%{query}%"))
        )
        providers_ids = [row[0] for row in providers_result.scalars().all()]

        return SearchResult(games=games_ids, providers=providers_ids)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return result