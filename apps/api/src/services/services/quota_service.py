from datetime import datetime, timedelta
from typing import Dict, Optional
import redis

class QuotaService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_quota = {
            'tokens_per_day': 100000,
            'requests_per_minute': 60
        }
    
    async def check_quota(self, user_id: str, provider: str) -> bool:
        """Verifica se o utilizador ainda tem quota disponível."""
        daily_key = f"quota:{user_id}:{provider}:daily:{datetime.now().date()}"
        minute_key = f"quota:{user_id}:{provider}:minute:{datetime.now().minute}"
        
        # Verifica quota diária
        daily_usage = int(self.redis.get(daily_key) or 0)
        if daily_usage >= self.default_quota['tokens_per_day']:
            return False
        
        # Verifica taxa por minuto
        minute_usage = int(self.redis.get(minute_key) or 0)
        if minute_usage >= self.default_quota['requests_per_minute']:
            return False
        
        return True
    
    async def update_usage(self, user_id: str, provider: str, tokens_used: int):
        """Atualiza o uso de tokens do utilizador."""
        daily_key = f"quota:{user_id}:{provider}:daily:{datetime.now().date()}"
        minute_key = f"quota:{user_id}:{provider}:minute:{datetime.now().minute}"
        
        # Atualiza contadores
        self.redis.incrby(daily_key, tokens_used)
        self.redis.incr(minute_key)
        
        # Define TTL
        self.redis.expire(daily_key, 86400)  # 24 horas
        self.redis.expire(minute_key, 60)    # 1 minuto 