# app/api/endpoints/search.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Game, Provider
from app.schemas.search import SearchResult

router = APIRouter()

@router.get("/search/", response_model=SearchResult)
async def search(
    query: Optional[str] = Query(None, min_length=2, max_length=100),
    db: AsyncSession = Depends(get_db)
):
    result = SearchResult()

    if query:
        # Поиск игр
        games_stmt = select(Game.id).where(Game.title.ilike(f"%{query}%"))
        games_result = await db.execute(games_stmt)
        result.games = [row[0] for row in games_result.fetchall()]

        # Поиск провайдеров
        providers_stmt = select(Provider.id).where(Provider.name.ilike(f"%{query}%"))
        providers_result = await db.execute(providers_stmt)
        result.providers = [row[0] for row in providers_result.fetchall()]

    return result
