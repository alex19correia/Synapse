"""Test configuration and fixtures."""
import pytest
import httpx
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from src.config.test_settings import test_settings
from src.main import app

# FastAPI test client
@pytest.fixture
def client() -> Generator:
    """Get FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client

# Async HTTP client
@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Get async HTTP client."""
    async with httpx.AsyncClient(
        app=app,
        base_url=f"http://{test_settings.api_host}:{test_settings.api_port}"
    ) as client:
        yield client

# Redis client for tests
@pytest.fixture
async def redis() -> AsyncGenerator[Redis, None]:
    """Get Redis client for tests."""
    client = Redis.from_url(test_settings.test_redis_url)
    try:
        yield client
    finally:
        await client.close()

# Test settings
@pytest.fixture
def settings():
    """Get test settings."""
    return test_settings 