from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.db.session import get_db
from app.schemas.search import SearchResult
from app.services.search_service import search_service

router = APIRouter()


@router.get("/search/", response_model=SearchResult)
async def search(
    query: str = Query(..., min_length=2, max_length=100, description="Search string"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Search games by title (cached in Redis)."""
    return await search_service.search(db, query)

