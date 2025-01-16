from redis import Redis
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException

class MetricsRateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis
        # Limites por minuto
        self.limits = {
            'error': 1000,    # Métricas de erro são críticas
            'batch': 100,     # Batches por minuto
            'default': 500    # Outras métricas individuais
        }
        self.window = 60  # 1 minuto

    async def check_rate_limit(
        self, 
        metric_type: str, 
        is_batch: bool = False,
        batch_size: Optional[int] = None
    ) -> None:
        """
        Verifica se a requisição está dentro do rate limit.
        Lança HTTPException se exceder o limite.
        """
        now = datetime.now().timestamp()
        window_start = int(now)
        
        # Define a chave e limite baseado no tipo
        if is_batch:
            key = f"metrics:ratelimit:batch:{window_start}"
            limit = self.limits['batch']
        elif metric_type == 'error':
            key = f"metrics:ratelimit:error:{window_start}"
            limit = self.limits['error']
        else:
            key = f"metrics:ratelimit:default:{window_start}"
            limit = self.limits['default']

        # Incrementa o contador
        current = await self.redis.incr(key)
        
        # Define TTL na primeira chamada
        if current == 1:
            await self.redis.expire(key, self.window)

        # Para batches, multiplica pelo tamanho
        if is_batch and batch_size:
            current = current * batch_size

        # Verifica se excedeu o limite
        if current > limit:
            retry_after = self.window - (int(now) % self.window)
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={'Retry-After': str(retry_after)}
            ) 