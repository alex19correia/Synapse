"""
Rate limiter implementation for the crawler.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

class RateLimiter:
    """
    Rate limiter for controlling request frequency.
    """
    
    def __init__(self, rate_limit: int = 10, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit: Maximum requests per period
            period: Time period in seconds
        """
        self.rate_limit = rate_limit
        self.period = period
        self.requests: Dict[str, datetime] = {}
        self.lock = asyncio.Lock()
        
    async def acquire(self, domain: Optional[str] = None) -> None:
        """
        Acquire a rate limit slot.
        
        Args:
            domain: Optional domain for domain-specific rate limiting
        """
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.period)
            
            # Clean old requests
            self.requests = {
                ts: dt for ts, dt in self.requests.items()
                if dt > cutoff
            }
            
            # Check rate limit
            if len(self.requests) >= self.rate_limit:
                oldest = min(self.requests.values())
                sleep_time = (oldest + timedelta(seconds=self.period) - now).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            # Add new request
            self.requests[str(now.timestamp())] = now 