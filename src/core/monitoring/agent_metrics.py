from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel
import prometheus_client as prom
import time

class LatencyTracker:
    def __init__(self, histogram, labels):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.histogram.labels(**self.labels).observe(duration)

class AgentMetrics:
    """Sistema de métricas para agentes."""
    
    def __init__(self):
        # Contadores Prometheus
        self.query_counter = prom.Counter(
            'agent_queries_total',
            'Total de queries por agente',
            ['agent_id', 'status']
        )
        
        self.latency_histogram = prom.Histogram(
            'agent_latency_seconds',
            'Latência de resposta do agente',
            ['agent_id', 'operation']
        )
        
        self.memory_usage = prom.Gauge(
            'agent_memory_usage_bytes',
            'Uso de memória por agente',
            ['agent_id']
        )
        
        # Cache local para métricas temporárias
        self._temp_metrics = {}
    
    async def record_query(self, agent_id: str, status: str = "success"):
        """Registra uma query processada."""
        self.query_counter.labels(agent_id=agent_id, status=status).inc()
    
    async def track_latency(self, agent_id: str, operation: str):
        """Context manager para tracking de latência."""
        return LatencyTracker(
            self.latency_histogram,
            {"agent_id": agent_id, "operation": operation}
        )
    
    async def update_memory_usage(self, agent_id: str, bytes_used: int):
        """Atualiza uso de memória."""
        self.memory_usage.labels(agent_id=agent_id).set(bytes_used) 