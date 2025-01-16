"""API metrics."""
from typing import Dict, Any, Optional
from datetime import datetime
from src.services.metrics_service import metrics_service

class APIMetrics:
    """API metrics."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    async def track_request(
        self,
        method: str,
        endpoint: str,
        status: str = "success",
        duration: Optional[float] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ) -> None:
        """Track API request metrics."""
        await metrics_service.track_request(
            endpoint=endpoint,
            method=method,
            status=status,
            duration=duration or 0
        )
    
    async def track_error(
        self,
        method: str,
        endpoint: str,
        error_type: str
    ) -> None:
        """Track API error metrics."""
        await metrics_service.track_request(
            endpoint=endpoint,
            method=method,
            status="error",
            duration=0
        )
    
    async def start_request(
        self,
        method: str,
        endpoint: str
    ) -> None:
        """Start tracking a request."""
        await metrics_service.start_request(
            method=method,
            endpoint=endpoint
        )
    
    async def end_request(
        self,
        method: str,
        endpoint: str
    ) -> None:
        """End tracking a request."""
        await metrics_service.end_request(
            method=method,
            endpoint=endpoint
        )
    
    async def set_rate_limit(
        self,
        endpoint: str,
        remaining: int
    ) -> None:
        """Set remaining rate limit."""
        await metrics_service.set_rate_limit(
            endpoint=endpoint,
            remaining=remaining
        ) 