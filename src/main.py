"""Main API module."""
import os
import sys
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.api.routes import health, chat
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.dependencies import get_current_user
from src.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Synapse API",
    description="AI-powered API for chat completions and document processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "config": {
            "model": settings.DEFAULT_MODEL,
            "host": settings.HOST,
            "port": settings.PORT
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="debug"
    )