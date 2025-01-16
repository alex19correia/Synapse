from contextlib import contextmanager
from typing import Generator, Optional
from prometheus_client import Counter, Histogram, Gauge
import time
from src.utils.logger import logger

class MonitoringService:
    def __init__(self):
        # Métricas de requisições
        self.request_counter = Counter(
            'llm_requests_total',
            'Total de requisições ao LLM',
            ['model', 'status']
        )
        
        self.latency_histogram = Histogram(
            'llm_request_duration_seconds',
            'Latência das requisições ao LLM',
            ['model'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
        )
        
        # Métricas de tokens
        self.token_counter = Counter(
            'llm_tokens_total',
            'Total de tokens processados',
            ['model', 'type']  # type: prompt ou completion
        )
        
        # Métricas de cache
        self.cache_hits = Counter(
            'llm_cache_hits_total',
            'Total de hits no cache'
        )
        
        self.cache_misses = Counter(
            'llm_cache_misses_total',
            'Total de misses no cache'
        )
        
        # Métricas de erros
        self.error_counter = Counter(
            'llm_errors_total',
            'Total de erros por tipo',
            ['model', 'error_type']
        )
        
        # Métricas de custos (estimativa)
        self.cost_gauge = Gauge(
            'llm_estimated_cost_usd',
            'Custo estimado do uso do LLM em USD'
        )
    
    @contextmanager
    def track_request(self, model: str) -> Generator[None, None, None]:
        """Contexto para tracking automático de métricas de request"""
        start_time = time.time()
        try:
            yield
            self.request_counter.labels(model=model, status="success").inc()
        except Exception as e:
            self.request_counter.labels(model=model, status="error").inc()
            self.error_counter.labels(
                model=model,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            self.latency_histogram.labels(model=model).observe(duration)
            
    def track_tokens(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Registra uso de tokens"""
        self.token_counter.labels(model=model, type="prompt").inc(prompt_tokens)
        self.token_counter.labels(model=model, type="completion").inc(completion_tokens)
        
        # Estimar custo (exemplo para Deepseek)
        prompt_cost = (prompt_tokens / 1000) * 0.0002  # $0.0002 por 1k tokens
        completion_cost = (completion_tokens / 1000) * 0.0002
        self.cost_gauge.inc(prompt_cost + completion_cost)
    
    def track_cache(self, hit: bool):
        """Registra hit/miss do cache"""
        if hit:
            self.cache_hits.inc()
        else:
            self.cache_misses.inc()
    
    def log_error(self, model: str, error: Exception):
        """Registra erro específico"""
        error_type = type(error).__name__
        self.error_counter.labels(
            model=model,
            error_type=error_type
        ).inc()
        logger.error(f"LLM Error [{model}] {error_type}: {str(error)}") 