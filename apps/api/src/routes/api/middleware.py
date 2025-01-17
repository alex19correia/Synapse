import time
from fastapi import Request
from .metrics import (
    REQUEST_COUNT, 
    REQUEST_LATENCY,
    ACTIVE_USERS,
    MESSAGES_PROCESSED
)

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Métricas básicas de request
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)
    
    # Métricas específicas para rotas de chat
    if request.url.path.startswith("/chat"):
        if request.method == "POST":
            MESSAGES_PROCESSED.inc()
    
    return response 