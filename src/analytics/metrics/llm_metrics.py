"""LLM metrics module for tracking LLM performance and behavior."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger("llm_metrics")

class LLMMetrics:
    """LLM metrics tracking system."""
    
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
            'llm_requests_total',
            'Total number of LLM requests',
            ['model', 'endpoint', 'status']
        )
        
        self.errors_total = Counter(
            'llm_errors_total',
            'Total number of LLM errors',
            ['model', 'endpoint', 'error_type']
        )
        
        # Request tracking
        self.active_requests = Gauge(
            'llm_active_requests',
            'Number of currently active requests',
            ['model', 'endpoint']
        )
        
        # Rate limit tracking
        self.rate_limit_remaining = Gauge(
            'llm_rate_limit_remaining',
            'Number of requests remaining before rate limit',
            ['model']
        )
        
        # Performance metrics
        self.request_duration = Histogram(
            'llm_request_duration_seconds',
            'Request duration in seconds',
            ['model', 'endpoint'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
        )
        
        self.token_counts = Histogram(
            'llm_token_counts',
            'Token counts for requests',
            ['model', 'endpoint', 'token_type'],
            buckets=(10, 50, 100, 500, 1000, 5000, float('inf'))
        )
        
        self.response_length = Histogram(
            'llm_response_length',
            'Response length in characters',
            ['model', 'endpoint'],
            buckets=(100, 500, 1000, 5000, 10000, float('inf'))
        )
        
        self.initialized = True
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None
    
    async def track_request(
        self,
        model: str,
        endpoint: str,
        status: str = "success",
        duration: Optional[float] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        response_length: Optional[int] = None
    ):
        """Track an LLM request with optional metrics."""
        self.requests_total.labels(
            model=model,
            endpoint=endpoint,
            status=status
        ).inc()
        
        if duration is not None:
            self.request_duration.labels(
                model=model,
                endpoint=endpoint
            ).observe(duration)
            
        if prompt_tokens is not None:
            self.token_counts.labels(
                model=model,
                endpoint=endpoint,
                token_type="prompt"
            ).observe(prompt_tokens)
            
        if completion_tokens is not None:
            self.token_counts.labels(
                model=model,
                endpoint=endpoint,
                token_type="completion"
            ).observe(completion_tokens)
            
        if total_tokens is not None:
            self.token_counts.labels(
                model=model,
                endpoint=endpoint,
                token_type="total"
            ).observe(total_tokens)
            
        if response_length is not None:
            self.response_length.labels(
                model=model,
                endpoint=endpoint
            ).observe(response_length)
    
    async def track_error(self, model: str, endpoint: str, error_type: str):
        """Track an LLM error."""
        self.errors_total.labels(
            model=model,
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    async def start_request(self, model: str, endpoint: str):
        """Increment the active requests counter for a model/endpoint."""
        self.active_requests.labels(
            model=model,
            endpoint=endpoint
        ).inc()
    
    async def end_request(self, model: str, endpoint: str):
        """Decrement the active requests counter for a model/endpoint."""
        self.active_requests.labels(
            model=model,
            endpoint=endpoint
        ).dec()
    
    async def set_rate_limit(self, model: str, remaining: int):
        """Set the remaining rate limit for a model."""
        self.rate_limit_remaining.labels(
            model=model
        ).set(remaining) 