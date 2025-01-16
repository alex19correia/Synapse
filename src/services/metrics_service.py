from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from prometheus_client import Counter, Histogram, Gauge

@dataclass
class ChunkMetrics:
    total_chunks: int
    avg_chunk_size: int
    overlap_ratio: float
    processing_time_ms: float
    timestamp: datetime = datetime.now()

@dataclass
class RAGMetrics:
    query_time_ms: float
    num_results: int
    avg_similarity: float
    cache_hit: bool
    timestamp: datetime = datetime.now()

@dataclass
class PerformanceMetrics:
    endpoint: str
    method: str
    status: int
    latency_ms: float
    memory_usage_mb: float
    timestamp: datetime = datetime.now()

class MetricsService:
    def __init__(self):
        self.chunk_metrics: List[ChunkMetrics] = []
        self.rag_metrics: List[RAGMetrics] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        
        # Prometheus metrics
        self.request_counter = Counter(
            'api_requests_total',
            'Total de requisições à API',
            ['endpoint', 'method', 'status']
        )
        
        self.request_latency = Histogram(
            'api_request_duration_seconds',
            'Request duration in seconds',
            ['endpoint']
        )
        
        self.memory_gauge = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.active_users_gauge = Gauge(
            'active_users',
            'Number of active users'
        )
        
        self.rate_limit_gauge = Gauge(
            'rate_limit_remaining',
            'Remaining rate limit',
            ['endpoint']
        )
    
    async def track_request(self, endpoint: str, method: str, status: str, duration: float):
        """Track API request metrics."""
        self.request_counter.labels(endpoint=endpoint, method=method, status=status).inc()
        self.request_latency.labels(endpoint=endpoint).observe(duration)
        
        self.performance_metrics.append(PerformanceMetrics(
            endpoint=endpoint,
            method=method,
            status=int(status),
            latency_ms=duration * 1000,
            memory_usage_mb=0  # TODO: Implement memory tracking
        ))
    
    async def track_rag_query(self, query_time_ms: float, num_results: int, avg_similarity: float, cache_hit: bool):
        """Track RAG query metrics."""
        self.rag_metrics.append(RAGMetrics(
            query_time_ms=query_time_ms,
            num_results=num_results,
            avg_similarity=avg_similarity,
            cache_hit=cache_hit
        ))
    
    async def track_chunking(self, total_chunks: int, avg_chunk_size: int, overlap_ratio: float, processing_time_ms: float):
        """Track document chunking metrics."""
        self.chunk_metrics.append(ChunkMetrics(
            total_chunks=total_chunks,
            avg_chunk_size=avg_chunk_size,
            overlap_ratio=overlap_ratio,
            processing_time_ms=processing_time_ms
        ))
    
    async def set_active_users(self, count: int):
        """Set number of active users."""
        self.active_users_gauge.set(count)
    
    async def set_rate_limit(self, endpoint: str, remaining: int):
        """Set remaining rate limit."""
        self.rate_limit_gauge.labels(endpoint=endpoint).set(remaining)
    
    async def start_request(self, method: str, endpoint: str):
        """Start tracking a request."""
        pass  # TODO: Implement request tracking
    
    async def end_request(self, method: str, endpoint: str):
        """End tracking a request."""
        pass  # TODO: Implement request tracking

# Global instance
metrics_service = MetricsService() 