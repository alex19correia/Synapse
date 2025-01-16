from typing import Optional, Any
import json
import redis.asyncio as redis
from src.utils.logger import get_logger

logger = get_logger("cache")

class CacheService:
    """Service for handling caching operations."""
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from cache: {e}")
            return None
            
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in cache: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from cache: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in cache: {e}")
            return False
            
    async def ttl(self, key: str) -> Optional[int]:
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key} from cache: {e}")
            return None 