"""API metrics module for tracking request and performance metrics."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger("api_metrics")

# Global metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['path', 'method', 'status_code']
)

CLIENT_ERRORS = Counter(
    'api_client_errors_total',
    'Total number of 4xx client errors'
)

SERVER_ERRORS = Counter(
    'api_server_errors_total',
    'Total number of 5xx server errors'
)

RATE_LIMITS = Counter(
    'api_rate_limits_total',
    'Total number of rate limit checks',
    ['path', 'allowed']
)

CONCURRENT_REQUESTS = Gauge(
    'api_concurrent_requests',
    'Number of currently active requests'
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Request latency in seconds',
    ['path', 'method'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float('inf'))
)

REQUEST_SIZE = Histogram(
    'api_request_size_bytes',
    'Size of requests in bytes',
    ['path'],
    buckets=(100, 1000, 10000, 100000, float('inf'))
)

RESPONSE_SIZE = Histogram(
    'api_response_size_bytes',
    'Size of responses in bytes',
    ['path'],
    buckets=(100, 1000, 10000, 100000, float('inf'))
)

# Chat-specific metrics
ACTIVE_USERS = Gauge(
    'chat_active_users',
    'Number of currently active chat users'
)

MESSAGES_PROCESSED = Counter(
    'chat_messages_processed',
    'Total number of chat messages processed'
)

class APIMetrics:
    """API metrics tracking system."""
    
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
            
        self.initialized = True
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None
    
    async def track_request(self, path: str, method: str, status_code: int, duration: float):
        """Track an API request with its duration and status code."""
        # Track request count
        REQUEST_COUNT.labels(
            path=path,
            method=method,
            status_code=str(status_code)
        ).inc()
        
        # Track errors
        if 400 <= status_code < 500:
            CLIENT_ERRORS.inc()
        elif status_code >= 500:
            SERVER_ERRORS.inc()
            
        # Track latency
        REQUEST_LATENCY.labels(
            path=path,
            method=method
        ).observe(duration)
    
    async def start_request(self, method: str, endpoint: str):
        """Increment the concurrent requests counter."""
        CONCURRENT_REQUESTS.inc()
    
    async def end_request(self, method: str, endpoint: str):
        """Decrement the concurrent requests counter."""
        CONCURRENT_REQUESTS.dec()
    
    async def track_rate_limit(self, path: str, allowed: bool):
        """Track rate limit checks."""
        RATE_LIMITS.labels(
            path=path,
            allowed=str(allowed).lower()
        ).inc()
    
    async def track_request_size(self, path: str, size: int):
        """Track request size."""
        REQUEST_SIZE.labels(path=path).observe(size)
    
    async def track_response_size(self, path: str, size: int):
        """Track response size."""
        RESPONSE_SIZE.labels(path=path).observe(size)