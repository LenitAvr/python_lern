import pytest
from httpx import AsyncClient
from app.main import app
from app.core.cache import cache


@pytest.mark.asyncio
async def test_search_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/search/?q=test")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_cache_invalidation():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Очистка кеша
        response = await client.delete("/api/v1/search/cache/?q=test")
        assert response.status_code == 200

        # Очистка всего кеша
        response = await client.delete("/api/v1/search/cache/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "redis_connected" in data