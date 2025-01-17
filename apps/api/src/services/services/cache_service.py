import redis
import json
from typing import Any, Optional
from src.services.analytics import AnalyticsService
import hashlib
from redis.asyncio import Redis

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        
    async def get(self, key: str) -> Optional[str]:
        """
        Obtém item do cache
        """
        return await self.redis.get(key)
        
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """
        Guarda item no cache com TTL
        """
        return await self.redis.set(key, value, ex=ttl)
        
    def _generate_cache_key(self, prompt: str, context: dict) -> str:
        """
        Gera chave única para o cache baseada no prompt e contexto
        """
        context_hash = hashlib.md5(json.dumps(context).encode()).hexdigest()
        return f"llm:response:{context_hash}:{hashlib.md5(prompt.encode()).hexdigest()}" 