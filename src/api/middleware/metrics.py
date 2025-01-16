from prometheus_client import Counter, Histogram, Gauge
from prometheus_client.exposition import generate_latest
from fastapi import FastAPI, Request, Response
from time import time

# Métricas
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint']
)

ACTIVE_USERS = Gauge(
    'synapse_active_users',
    'Number of active users'
)

def setup_metrics(app: FastAPI):
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        duration = time() - start_time
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            endpoint=request.url.path
        ).observe(duration)
        
        return response

    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type="text/plain") 