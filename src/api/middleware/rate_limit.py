"""Rate limiting middleware."""
from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    _instance = None
    _requests = defaultdict(list)
    
    def __init__(self, app, rate_limit: int = 100, time_window: int = 60):
        """Initialize middleware.
        
        Args:
            app: FastAPI app
            rate_limit: Maximum number of requests per time window
            time_window: Time window in seconds
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        RateLimitMiddleware._instance = self
        
    @classmethod
    def reset(cls):
        """Reset rate limiter state."""
        if cls._instance:
            cls._requests.clear()
        
    async def dispatch(self, request: Request, call_next):
        """Process the request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            FastAPI response
        """
        client_ip = request.client.host
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Remove old requests
        RateLimitMiddleware._requests[client_ip] = [
            req_time for req_time in RateLimitMiddleware._requests[client_ip]
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(RateLimitMiddleware._requests[client_ip]) >= self.rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add request
        RateLimitMiddleware._requests[client_ip].append(now)
        
        # Process request
        return await call_next(request)
