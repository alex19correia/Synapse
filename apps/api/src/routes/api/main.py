"""Main API module."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram
from src.api.routes import health, chat
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.dependencies import get_current_user

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

app = FastAPI(
    title="Synapse API",
    description="API for Synapse LLM service",
    version="0.1.0"
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,
    time_window=60
)

# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(
    health.router,
    prefix="/api",
    tags=["health"]
)

# Protected chat routes
app.include_router(
    chat.router,
    prefix="/api",
    tags=["chat"],
    dependencies=[Depends(get_current_user)]
)

# Test routes without auth
app.include_router(
    chat.router,
    prefix="/api/test",
    tags=["test"]
)

# Root health check for Prometheus
@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"status": "ok"}

# Health check route
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}