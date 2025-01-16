"""Unit tests for the cache service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import json
from typing import Any, Dict

from src.core.cache import CacheService

@pytest.fixture
def mock_redis():
    """Create a mock Redis instance."""
    mock = MagicMock()
    mock.get = AsyncMock()
    mock.set = AsyncMock()
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    mock.exists = AsyncMock()
    mock.ttl = AsyncMock()
    return mock

@pytest.fixture
def cache_service(mock_redis, monkeypatch):
    """Create a CacheService instance with a mock Redis client."""
    monkeypatch.setattr('redis.asyncio.from_url', lambda x: mock_redis)
    return CacheService()

@pytest.fixture
def sample_data() -> Dict[str, Any]:
    """Create sample data for testing."""
    return {
        'id': '123',
        'name': 'test',
        'data': {
            'key': 'value',
            'number': 42,
            'list': [1, 2, 3]
        }
    }

@pytest.mark.asyncio
async def test_get_existing_key(cache_service, mock_redis, sample_data):
    """Test retrieving an existing key from cache."""
    # Arrange
    key = "test-key"
    mock_redis.get.return_value = json.dumps(sample_data).encode()

    # Act
    result = await cache_service.get(key)

    # Assert
    assert result == sample_data
    mock_redis.get.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_get_nonexistent_key(cache_service, mock_redis):
    """Test retrieving a nonexistent key from cache."""
    # Arrange
    key = "nonexistent-key"
    mock_redis.get.return_value = None

    # Act
    result = await cache_service.get(key)

    # Assert
    assert result is None
    mock_redis.get.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_get_invalid_json(cache_service, mock_redis):
    """Test handling invalid JSON data in cache."""
    # Arrange
    key = "invalid-json-key"
    mock_redis.get.return_value = b"invalid json"

    # Act
    result = await cache_service.get(key)

    # Assert
    assert result is None
    mock_redis.get.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_set_without_ttl(cache_service, mock_redis, sample_data):
    """Test setting a key without TTL."""
    # Arrange
    key = "test-key"
    
    # Act
    success = await cache_service.set(key, sample_data)

    # Assert
    assert success is True
    mock_redis.set.assert_called_once_with(
        key,
        json.dumps(sample_data)
    )

@pytest.mark.asyncio
async def test_set_with_ttl(cache_service, mock_redis, sample_data):
    """Test setting a key with TTL."""
    # Arrange
    key = "test-key"
    ttl = 3600
    
    # Act
    success = await cache_service.set(key, sample_data, ttl)

    # Assert
    assert success is True
    mock_redis.setex.assert_called_once_with(
        key,
        ttl,
        json.dumps(sample_data)
    )

@pytest.mark.asyncio
async def test_set_error_handling(cache_service, mock_redis, sample_data):
    """Test error handling when setting a key."""
    # Arrange
    key = "test-key"
    mock_redis.set.side_effect = Exception("Redis error")

    # Act
    success = await cache_service.set(key, sample_data)

    # Assert
    assert success is False
    mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_delete_existing_key(cache_service, mock_redis):
    """Test deleting an existing key."""
    # Arrange
    key = "test-key"
    mock_redis.delete.return_value = 1

    # Act
    success = await cache_service.delete(key)

    # Assert
    assert success is True
    mock_redis.delete.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_delete_nonexistent_key(cache_service, mock_redis):
    """Test deleting a nonexistent key."""
    # Arrange
    key = "nonexistent-key"
    mock_redis.delete.return_value = 0

    # Act
    success = await cache_service.delete(key)

    # Assert
    assert success is True  # Redis delete is idempotent
    mock_redis.delete.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_exists_true(cache_service, mock_redis):
    """Test checking existence of an existing key."""
    # Arrange
    key = "test-key"
    mock_redis.exists.return_value = 1

    # Act
    exists = await cache_service.exists(key)

    # Assert
    assert exists is True
    mock_redis.exists.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_exists_false(cache_service, mock_redis):
    """Test checking existence of a nonexistent key."""
    # Arrange
    key = "nonexistent-key"
    mock_redis.exists.return_value = 0

    # Act
    exists = await cache_service.exists(key)

    # Assert
    assert exists is False
    mock_redis.exists.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_ttl_existing_key(cache_service, mock_redis):
    """Test getting TTL of an existing key."""
    # Arrange
    key = "test-key"
    mock_redis.ttl.return_value = 3600

    # Act
    ttl = await cache_service.ttl(key)

    # Assert
    assert ttl == 3600
    mock_redis.ttl.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_ttl_nonexistent_key(cache_service, mock_redis):
    """Test getting TTL of a nonexistent key."""
    # Arrange
    key = "nonexistent-key"
    mock_redis.ttl.return_value = -2  # Redis returns -2 for nonexistent keys

    # Act
    ttl = await cache_service.ttl(key)

    # Assert
    assert ttl == -2
    mock_redis.ttl.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_ttl_persistent_key(cache_service, mock_redis):
    """Test getting TTL of a persistent key (no expiration)."""
    # Arrange
    key = "persistent-key"
    mock_redis.ttl.return_value = -1  # Redis returns -1 for persistent keys

    # Act
    ttl = await cache_service.ttl(key)

    # Assert
    assert ttl == -1
    mock_redis.ttl.assert_called_once_with(key)