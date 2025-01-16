from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any

# Métricas de LLM
llm_requests_total = Counter(
    'llm_requests_total',
    'Total number of LLM requests',
    ['model', 'status']
)

llm_response_time = Histogram(
    'llm_response_time_seconds',
    'Time spent processing LLM requests',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

llm_token_usage = Counter(
    'llm_token_usage_total',
    'Total tokens used by LLM requests',
    ['model', 'type']
)

# Métricas de Cache
cache_requests = Counter(
    'cache_requests_total',
    'Total cache requests',
    ['type']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['type']
)

# Métricas de Usuário
user_messages = Counter(
    'user_messages_total',
    'Total messages sent by users',
    ['user_id']
)

user_session_duration = Histogram(
    'user_session_duration_seconds',
    'Duration of user sessions',
    ['user_id'],
    buckets=[60, 300, 900, 1800, 3600]
)

# Métricas de Sistema
memory_usage = Gauge(
    'memory_usage_bytes',
    'Current memory usage',
    ['component']
)

error_rate = Counter(
    'errors_total',
    'Total number of errors',
    ['type', 'component']
)

# Métricas de Logs
log_entries = Counter(
    'log_entries_total',
    'Total number of log entries',
    ['level', 'component']
)

log_errors = Counter(
    'log_errors_total',
    'Total number of error logs',
    ['component']
)

# Métricas de API
api_requests = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['path', 'method', 'status']
)

api_response_time = Histogram(
    'api_response_time_seconds',
    'Time spent processing API requests',
    ['path', 'method'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

# Métricas de Duração
duration_histogram = Histogram(
    'operation_duration_seconds',
    'Duration of various operations',
    ['component'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

class MetricsCollector:
    """Coletor centralizado de métricas"""
    
    @staticmethod
    def track_llm_request(model: str, duration: float, tokens: int, success: bool):
        """Registra métricas de request LLM"""
        status = 'success' if success else 'error'
        llm_requests_total.labels(model=model, status=status).inc()
        llm_response_time.labels(model=model).observe(duration)
        llm_token_usage.labels(model=model, type='total').inc(tokens)
    
    @staticmethod
    def track_cache_operation(operation_type: str, hit: bool):
        """Registra métricas de cache"""
        cache_requests.labels(type=operation_type).inc()
        if hit:
            cache_hits.labels(type=operation_type).inc()
    
    @staticmethod
    def track_user_activity(user_id: str, session_duration: float):
        """Registra métricas de atividade do usuário"""
        user_messages.labels(user_id=user_id).inc()
        user_session_duration.labels(user_id=user_id).observe(session_duration)
    
    @staticmethod
    def update_memory_usage(component: str, usage: float):
        """Atualiza métricas de uso de memória"""
        memory_usage.labels(component=component).set(usage)
    
    @staticmethod
    def track_error(error_type: str, component: str):
        """Registra métricas de erro"""
        error_rate.labels(type=error_type, component=component).inc()

    @staticmethod
    def track_log(data: Dict[str, Any]):
        """Registra métricas de logs"""
        level = data.get('level', 'unknown')
        component = data.get('component', 'unknown')
        
        # Incrementa contador geral de logs
        log_entries.labels(level=level, component=component).inc()
        
        # Se for erro, incrementa contador específico
        if data.get('hasError'):
            log_errors.labels(component=component).inc()

    @staticmethod
    def track_api_request(data: Dict[str, Any]):
        """Registra métricas de requisições API"""
        path = data.get('path', 'unknown')
        method = data.get('method', 'unknown')
        status = str(data.get('statusCode', 500))
        duration = data.get('duration', 0.0)

        # Incrementa contador de requisições
        api_requests.labels(
            path=path,
            method=method,
            status=status
        ).inc()

        # Registra tempo de resposta
        api_response_time.labels(
            path=path,
            method=method
        ).observe(duration)

    @staticmethod
    def track_duration(component: str, duration: float):
        """Registra duração de operações"""
        duration_histogram.labels(component=component).observe(duration) 