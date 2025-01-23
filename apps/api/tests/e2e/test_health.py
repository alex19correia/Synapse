"""E2E tests for health check endpoint."""
import pytest
from loguru import logger

pytestmark = pytest.mark.asyncio

async def test_health_check(async_client):
    """Test health check endpoint."""
    logger.info("Testing health check endpoint...")
    
    # When: Making a request to the health endpoint
    response = await async_client.get("/health")
    
    # Then: Response should be successful
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    
    logger.info("✅ Health check test passed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_health_check()) 