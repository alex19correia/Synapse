from typing import Any, Optional, Union
import json
from redis import asyncio as aioredis
from pydantic import BaseModel
from ..config.settings import get_settings

class CacheConfig(BaseModel):
    ttl: int = 3600  # 1 hora default
    namespace: str
    version: str = "v1"

class RedisCache:
    def __init__(self, namespace: str, ttl: int = 3600):
        self.config = CacheConfig(namespace=namespace, ttl=ttl)
        settings = get_settings()
        self.redis = aioredis.from_url(settings.redis_url)

    def _get_key(self, key: str) -> str:
        """Gera chave com namespace e versão"""
        return f"{self.config.namespace}:{self.config.version}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        try:
            full_key = self._get_key(key)
            if value := await self.redis.get(full_key):
                return json.loads(value)
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        try:
            full_key = self._get_key(key)
            ttl = ttl or self.config.ttl
            await self.redis.setex(
                full_key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao definir cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            full_key = self._get_key(key)
            await self.redis.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cache: {e}")
            return False

    async def clear_namespace(self) -> bool:
        """Limpa todo cache do namespace"""
        try:
            pattern = f"{self.config.namespace}:{self.config.version}:*"
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, pattern)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar namespace: {e}")
            return False 