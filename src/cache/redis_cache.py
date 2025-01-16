import os
import redis
from typing import Any, Optional

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[str]:
        return self.redis.get(key)

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        return self.redis.set(key, value, ex=expire) 