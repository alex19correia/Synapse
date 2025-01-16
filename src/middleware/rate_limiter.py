from fastapi import Request, HTTPException
import redis
from typing import Optional

class RateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_limits = {
            "general": {"rate": 100, "per": 60},  # 100 requests/minute
            "chat": {"rate": 20, "per": 60},      # 20 requests/minute
            "auth": {"rate": 5, "per": 60}        # 5 requests/minute
        }
    
    async def check_rate_limit(self, request: Request, limit_type: str = "general"):
        client_ip = request.client.host
        key = f"rate_limit:{limit_type}:{client_ip}"
        
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, self.default_limits[limit_type]["per"])
            
        if current > self.default_limits[limit_type]["rate"]:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            ) 