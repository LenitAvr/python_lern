"""
Сервис поиска: только id-игры и id-провайдера, кеш Redis.
"""
from __future__ import annotations

# import json
import logging
# from typing import Any, Dict, List

from sqlalchemy import select, distinct, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Game, Provider
from app.core.cache import cache
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self) -> None:
        self.ttl = settings.CACHE_TTL

    async def search(self, db: AsyncSession, query: str) -> dict:
        query_clean = query.strip().lower()
        cache_key = f"search:{query_clean}"

        # кеш
        try:
            cached: dict | None = await cache.get(cache_key)
            if cached is not None:
                logger.info("Cache hit for key=%s", cache_key)
                return cached
            logger.info("Cache miss for key=%s", cache_key)
        except Exception as exc:
            logger.warning("Redis get error: %s", exc)

        # БД
        games, providers = await self._fetch_data(db, query_clean)

        result = {"games": games, "providers": providers}

        # сохраняем в кеш
        try:
            await cache.set(cache_key, result, self.ttl)
        except Exception as exc:
            logger.warning("Redis set error: %s", exc)

        return result

    async def _fetch_data(self, db: AsyncSession, query_clean: str) -> tuple[list[int], list[int]]:
        like_pattern = f"%{query_clean}%"

        # --- ищем ПО ИГРЕ ---
        g_stmt = (
            select(Game.id)
            .where(Game.title.ilike(like_pattern))
            .order_by(Game.id)
        )
        games = [row[0] for row in (await db.execute(g_stmt)).all()]

        # --- ищем ПО ПРОВАЙДЕРУ ---
        p_stmt = (
            select(Provider.id)  # ← возвращаем id провайдера
            .where(Provider.name.ilike(like_pattern))
            .order_by(Provider.id)
        )
        providers = [row[0] for row in (await db.execute(p_stmt)).all()]

        # если ввели провайдера – можно не выводить игры
        # уберите if/else, если нужно «и то, и другое»
        if providers:
            games = []  # оставляем только провайдеров
        # иначе остаётся список игр, найденных по title

        return games, providers

    async def invalidate(self, query: str | None = None) -> None:
        if query:
            key = f"search:{query.strip().lower()}"
            await cache.delete(key)
        else:
            await cache.clear_pattern("search:*")


search_service = SearchService()