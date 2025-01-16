"""Crawler metrics module for tracking crawling performance and behavior."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger("crawler_metrics")

class CrawlerMetrics:
    """Crawler metrics tracking system."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None or not hasattr(cls._instance, 'initialized'):
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize metrics if not already initialized."""
        if self.initialized:
            return
            
        # Request counters
        self.requests_total = Counter(
            'crawler_requests_total',
            'Total number of crawler requests',
            ['source', 'endpoint', 'status']
        )
        
        self.errors_total = Counter(
            'crawler_errors_total',
            'Total number of crawler errors',
            ['source', 'endpoint', 'error_type']
        )
        
        # Request tracking
        self.active_requests = Gauge(
            'crawler_active_requests',
            'Number of currently active requests',
            ['source', 'endpoint']
        )
        
        # Rate limit tracking
        self.rate_limit_remaining = Gauge(
            'crawler_rate_limit_remaining',
            'Number of requests remaining before rate limit',
            ['source']
        )
        
        # Performance metrics
        self.request_duration = Histogram(
            'crawler_request_duration_seconds',
            'Request duration in seconds',
            ['source', 'endpoint'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
        )
        
        self.response_size = Histogram(
            'crawler_response_size_bytes',
            'Response size in bytes',
            ['source', 'endpoint'],
            buckets=(1000, 10000, 100000, 1000000, float('inf'))
        )
        
        self.initialized = True
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None
    
    async def track_request(
        self,
        source: str,
        endpoint: str,
        status: str = "success",
        duration: Optional[float] = None,
        response_size: Optional[int] = None
    ):
        """Track a crawler request with optional metrics."""
        self.requests_total.labels(
            source=source,
            endpoint=endpoint,
            status=status
        ).inc()
        
        if duration is not None:
            self.request_duration.labels(
                source=source,
                endpoint=endpoint
            ).observe(duration)
            
        if response_size is not None:
            self.response_size.labels(
                source=source,
                endpoint=endpoint
            ).observe(response_size)
    
    async def track_error(self, source: str, endpoint: str, error_type: str):
        """Track a crawler error."""
        self.errors_total.labels(
            source=source,
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    async def start_request(self, source: str, endpoint: str):
        """Increment the active requests counter for a source/endpoint."""
        self.active_requests.labels(
            source=source,
            endpoint=endpoint
        ).inc()
    
    async def end_request(self, source: str, endpoint: str):
        """Decrement the active requests counter for a source/endpoint."""
        self.active_requests.labels(
            source=source,
            endpoint=endpoint
        ).dec()
    
    async def set_rate_limit(self, source: str, remaining: int):
        """Set the remaining rate limit for a source."""
        self.rate_limit_remaining.labels(
            source=source
        ).set(remaining) 