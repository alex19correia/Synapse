from typing import Optional, Any
import json
import hashlib
from redis.asyncio import Redis
from pydantic import BaseModel

class CacheConfig(BaseModel):
    """Configuração do cache"""
    enabled: bool = True
    ttl: int = 3600  # 1 hora
    max_size: str = "1GB"

class DistributedCache:
    """Cache distribuído baseado em Redis"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost",
        config: Optional[CacheConfig] = None
    ):
        self.redis = Redis.from_url(redis_url)
        self.config = config or CacheConfig()
    
    def _get_key(self, url: str) -> str:
        """Gera chave única para URL"""
        return f"cache:{hashlib.sha256(url.encode()).hexdigest()}"
    
    async def get(self, url: str) -> Optional[dict]:
        """Recupera conteúdo do cache"""
        if not self.config.enabled:
            return None
            
        key = self._get_key(url)
        data = await self.redis.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def set(self, url: str, content: dict) -> None:
        """Armazena conteúdo no cache"""
        if not self.config.enabled:
            return
            
        key = self._get_key(url)
        data = json.dumps(content)
        
        await self.redis.set(
            key,
            data,
            ex=self.config.ttl
        )
    
    async def invalidate(self, url: str) -> None:
        """Invalida cache para uma URL"""
        if not self.config.enabled:
            return
            
        key = self._get_key(url)
        await self.redis.delete(key)
    
    async def clear(self) -> None:
        """Limpa todo o cache"""
        if not self.config.enabled:
            return
            
        await self.redis.flushdb()
    
    async def close(self):
        """Fecha conexão com Redis"""
        await self.redis.close() 