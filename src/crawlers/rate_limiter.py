from typing import Optional
import time
from redis.asyncio import Redis
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    """Configuração de rate limiting"""
    requests_per_second: int = 2
    max_requests_per_domain: int = 100
    cooldown_period: int = 60  # segundos

class RateLimiter:
    """Rate limiter baseado em Redis"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost",
        config: Optional[RateLimitConfig] = None
    ):
        self.redis = Redis.from_url(redis_url)
        self.config = config or RateLimitConfig()
    
    async def check_rate_limit(self, domain: str) -> bool:
        """Verifica se o domínio está dentro do rate limit"""
        now = int(time.time())
        pipe = self.redis.pipeline()
        
        # Chaves para controle
        domain_key = f"rate:domain:{domain}"
        global_key = "rate:global"
        
        # Adiciona timestamp atual
        pipe.zadd(domain_key, {str(now): now})
        pipe.zadd(global_key, {str(now): now})
        
        # Remove timestamps antigos
        min_time = now - self.config.cooldown_period
        pipe.zremrangebyscore(domain_key, 0, min_time)
        pipe.zremrangebyscore(global_key, 0, min_time)
        
        # Conta requests
        pipe.zcard(domain_key)
        pipe.zcard(global_key)
        
        # Executa pipeline
        results = await pipe.execute()
        domain_requests = results[-2]
        global_requests = results[-1]
        
        # Define TTL para as chaves
        await self.redis.expire(domain_key, self.config.cooldown_period)
        await self.redis.expire(global_key, self.config.cooldown_period)
        
        # Verifica limites
        if (domain_requests > self.config.max_requests_per_domain or
            global_requests > self.config.requests_per_second * self.config.cooldown_period):
            return False
        
        return True
    
    async def close(self):
        """Fecha conexão com Redis"""
        await self.redis.close() 