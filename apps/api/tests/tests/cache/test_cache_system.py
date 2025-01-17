import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.cache import Cache
from redis.asyncio.client import Redis
from redis.exceptions import RedisError

@pytest.fixture
def mock_redis():
    with patch("redis.asyncio.Redis") as mock:
        client = AsyncMock()
        mock.from_url.return_value = client
        yield client

@pytest.fixture
def cache(mock_redis):
    return Cache("redis://localhost")

@pytest.mark.asyncio
class TestCacheSystem:
    async def test_connection(self, cache, mock_redis):
        """Tests Redis connection setup."""
        assert cache.redis is not None
        mock_redis.ping.assert_not_called()  # Connection is lazy

        # Test connection on first operation
        await cache.get("test")
        mock_redis.ping.assert_called_once()

    async def test_set_get(self, cache, mock_redis):
        """Tests basic set/get operations."""
        # Setup
        mock_redis.get.return_value = b'{"value": "test_value"}'
        mock_redis.set.return_value = True

        # Test set
        success = await cache.set("test_key", "test_value")
        assert success is True
        mock_redis.set.assert_called_once()

        # Test get
        value = await cache.get("test_key")
        assert value == "test_value"
        mock_redis.get.assert_called_once_with("test_key")

    async def test_set_with_ttl(self, cache, mock_redis):
        """Tests setting values with TTL."""
        # Test set with TTL
        await cache.set("test_key", "test_value", ttl=3600)
        mock_redis.set.assert_called_once_with(
            "test_key",
            '{"value": "test_value"}',
            ex=3600
        )

    async def test_get_ttl(self, cache, mock_redis):
        """Tests TTL retrieval."""
        # Setup
        mock_redis.ttl.return_value = 3500  # 3500 seconds remaining

        # Test
        ttl = await cache.ttl("test_key")
        assert ttl == 3500
        mock_redis.ttl.assert_called_once_with("test_key")

    async def test_delete(self, cache, mock_redis):
        """Tests key deletion."""
        # Setup
        mock_redis.delete.return_value = 1

        # Test
        success = await cache.delete("test_key")
        assert success is True
        mock_redis.delete.assert_called_once_with("test_key")

    async def test_exists(self, cache, mock_redis):
        """Tests key existence check."""
        # Setup
        mock_redis.exists.return_value = 1

        # Test
        exists = await cache.exists("test_key")
        assert exists is True
        mock_redis.exists.assert_called_once_with("test_key")

    async def test_set_get_complex_data(self, cache, mock_redis):
        """Tests handling of complex data structures."""
        # Setup
        complex_data = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "bool": True,
            "null": None
        }
        mock_redis.get.return_value = b'{"value": {"string": "value", "number": 42, "list": [1, 2, 3], "dict": {"key": "value"}, "bool": true, "null": null}}'
        mock_redis.set.return_value = True

        # Test set
        success = await cache.set("complex_key", complex_data)
        assert success is True

        # Test get
        value = await cache.get("complex_key")
        assert value == complex_data

    async def test_concurrent_operations(self, cache, mock_redis):
        """Tests concurrent cache operations."""
        # Setup
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b'{"value": "test_value"}'

        # Test multiple concurrent operations
        tasks = [
            cache.set(f"key_{i}", f"value_{i}")
            for i in range(10)
        ] + [
            cache.get(f"key_{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == 20
        assert all(r is not None for r in results)

    async def test_error_handling(self, cache, mock_redis):
        """Tests error handling."""
        # Test connection error
        mock_redis.ping.side_effect = RedisError("Connection failed")
        with pytest.raises(RedisError):
            await cache.get("test_key")

        # Test set error
        mock_redis.set.side_effect = RedisError("Set failed")
        success = await cache.set("test_key", "value")
        assert success is False

        # Test get error
        mock_redis.get.side_effect = RedisError("Get failed")
        value = await cache.get("test_key")
        assert value is None

    async def test_cache_invalidation(self, cache, mock_redis):
        """Tests cache invalidation."""
        # Setup
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = [b"prefix_1", b"prefix_2"]

        # Test pattern deletion
        count = await cache.invalidate_pattern("prefix_*")
        assert count == 2
        mock_redis.keys.assert_called_once_with("prefix_*")
        assert mock_redis.delete.call_count == 1

    async def test_cache_metrics(self, cache, mock_redis):
        """Tests cache metrics collection."""
        # Setup
        mock_redis.info.return_value = {
            "used_memory": "1024",
            "connected_clients": "1",
            "keyspace_hits": "100",
            "keyspace_misses": "10"
        }

        # Test metrics collection
        metrics = await cache.get_metrics()
        assert metrics["memory_used"] == 1024
        assert metrics["connected_clients"] == 1
        assert metrics["hit_rate"] == 0.9090909090909091  # 100/(100+10)

    async def test_bulk_operations(self, cache, mock_redis):
        """Tests bulk cache operations."""
        # Setup
        mock_redis.mset.return_value = True
        mock_redis.mget.return_value = [
            b'{"value": "value1"}',
            b'{"value": "value2"}'
        ]

        # Test bulk set
        data = {
            "key1": "value1",
            "key2": "value2"
        }
        success = await cache.bulk_set(data)
        assert success is True

        # Test bulk get
        values = await cache.bulk_get(["key1", "key2"])
        assert values == ["value1", "value2"]

    async def test_cache_persistence(self, cache, mock_redis):
        """Tests cache persistence operations."""
        # Test save
        mock_redis.save.return_value = True
        success = await cache.save()
        assert success is True
        mock_redis.save.assert_called_once()

        # Test last save
        mock_redis.lastsave.return_value = 1234567890
        timestamp = await cache.last_save()
        assert timestamp == 1234567890
        mock_redis.lastsave.assert_called_once() 