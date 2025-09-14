import json
import logging
from typing import Optional, Any
from redis.asyncio import Redis
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RedisCache:
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.is_connected = False

    async def connect(self):
        try:
            self.redis = Redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True,
                password=settings.REDIS_PASSWORD or None,
            )
            await self.redis.ping()
            self.is_connected = True
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            self.redis = None

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.is_connected = False
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        if not self.is_connected or not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            if value:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(value)
            logger.info(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self.is_connected or not self.redis:
            return False
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
            logger.info(f"Cached key: {key} with TTL: {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.is_connected or not self.redis:
            return False
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        if not self.is_connected or not self.redis:
            return 0
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys with pattern: {pattern}")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0


cache = RedisCache()