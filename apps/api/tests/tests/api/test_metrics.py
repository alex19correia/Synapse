"""Tests for API metrics tracking."""

import pytest
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR
from src.api.metrics import APIMetrics
from unittest.mock import AsyncMock, patch
import time

@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the Prometheus registry before and after each test."""
    # Clear all collectors including default ones
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    
    # Reset the metrics singleton
    APIMetrics.reset()
    
    yield
    
    # Clean up after test
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    
    # Reset the metrics singleton
    APIMetrics.reset()

@pytest.fixture
def metrics(clear_registry):
    """Fixture for API metrics."""
    return APIMetrics()

@pytest.mark.asyncio
class TestAPIMetrics:
    async def test_request_tracking(self, metrics):
        """Tests basic request tracking."""
        await metrics.track_request(
            path="/test",
            method="GET",
            status_code=200,
            duration=0.1
        )
        
        # Verify metrics were recorded
        value = metrics.requests_total.labels(
            path="/test",
            method="GET",
            status_code="200"
        )._value.get()
        assert value == 1
        
        # Verify latency was recorded
        latency = metrics.request_latency.labels(
            path="/test",
            method="GET"
        )
        samples = list(latency._samples())
        assert len(samples) > 0
        assert any(s.name.endswith('_count') for s in samples)
        assert any(s.name.endswith('_sum') for s in samples)
    
    async def test_error_tracking(self, metrics):
        """Tests error tracking."""
        # Track 4xx error
        await metrics.track_request(
            path="/test",
            method="GET",
            status_code=404,
            duration=0.1
        )
        
        # Track 5xx error
        await metrics.track_request(
            path="/test",
            method="GET",
            status_code=500,
            duration=0.1
        )
        
        # Verify error counts
        client_errors = metrics.client_errors_total._value.get()
        server_errors = metrics.server_errors_total._value.get()
        
        assert client_errors == 1
        assert server_errors == 1
    
    async def test_concurrent_requests_tracking(self, metrics):
        """Tests tracking of concurrent requests."""
        # Start multiple requests
        await metrics.start_request()
        await metrics.start_request()
        
        value = metrics.concurrent_requests._value.get()
        assert value == 2
        
        # End requests
        await metrics.end_request()
        await metrics.end_request()
        
        value = metrics.concurrent_requests._value.get()
        assert value == 0
    
    async def test_rate_limit_tracking(self, metrics):
        """Tests rate limit metrics."""
        await metrics.track_rate_limit("/test", True)  # Allowed
        await metrics.track_rate_limit("/test", False)  # Blocked
        
        allowed = metrics.rate_limits_total.labels(
            path="/test",
            allowed="true"
        )._value.get()
        blocked = metrics.rate_limits_total.labels(
            path="/test",
            allowed="false"
        )._value.get()
        
        assert allowed == 1
        assert blocked == 1
    
    async def test_request_size_tracking(self, metrics):
        """Tests request size tracking."""
        sizes = [100, 500, 1000, 5000]
        
        for size in sizes:
            await metrics.track_request_size("/test", size)
        
        histogram = metrics.request_size.labels(path="/test")
        samples = list(histogram._samples())
        count_sample = next(s for s in samples if s.name.endswith('_count'))
        sum_sample = next(s for s in samples if s.name.endswith('_sum'))
        
        assert count_sample.value == len(sizes)
        assert sum_sample.value == sum(sizes)
    
    async def test_response_size_tracking(self, metrics):
        """Tests response size tracking."""
        sizes = [50, 200, 800, 2000]
        
        for size in sizes:
            await metrics.track_response_size("/test", size)
        
        histogram = metrics.response_size.labels(path="/test")
        samples = list(histogram._samples())
        count_sample = next(s for s in samples if s.name.endswith('_count'))
        sum_sample = next(s for s in samples if s.name.endswith('_sum'))
        
        assert count_sample.value == len(sizes)
        assert sum_sample.value == sum(sizes)
    
    async def test_endpoint_usage_patterns(self, metrics):
        """Tests tracking of endpoint usage patterns."""
        endpoints = ["/generate", "/summarize", "/extract-entities"]
        methods = ["GET", "POST"]
        
        for endpoint in endpoints:
            for method in methods:
                await metrics.track_request(
                    path=endpoint,
                    method=method,
                    status_code=200,
                    duration=0.1
                )
        
        # Verify each endpoint/method combination was tracked
        for endpoint in endpoints:
            for method in methods:
                value = metrics.requests_total.labels(
                    path=endpoint,
                    method=method,
                    status_code="200"
                )._value.get()
                assert value == 1
    
    async def test_latency_buckets(self, metrics):
        """Tests latency histogram buckets."""
        # Test values for each bucket
        latencies = [
            0.005,  # Should go in 0.01 bucket
            0.02,   # Should go in 0.05 bucket
            0.075,  # Should go in 0.1 bucket
            0.3,    # Should go in 0.5 bucket
            0.75    # Should go in 1.0 bucket
        ]
        
        for latency in latencies:
            await metrics.track_request(
                path="/test",
                method="GET",
                status_code=200,
                duration=latency
            )
        
        histogram = metrics.request_latency.labels(
            path="/test",
            method="GET"
        )
        samples = list(histogram._samples())
        count_sample = next(s for s in samples if s.name.endswith('_count'))
        sum_sample = next(s for s in samples if s.name.endswith('_sum'))
        bucket_samples = [s for s in samples if s.name.endswith('_bucket')]
        
        # Verify histogram recorded all values
        assert count_sample.value == len(latencies)
        assert abs(sum_sample.value - sum(latencies)) < 0.0001  # Use approximate equality for floats
        
        # Verify bucket distribution
        # Note: Prometheus histogram buckets are cumulative
        bucket_values = {float(s.labels['le']): s.value for s in bucket_samples}
        assert bucket_values[float('inf')] == len(latencies)  # All values
        assert bucket_values[0.01] == 1   # Just 0.005
        assert bucket_values[0.05] == 2   # 0.005 and 0.02
        assert bucket_values[0.1] == 3    # Previous plus 0.075
        assert bucket_values[0.5] == 4    # Previous plus 0.3
        assert bucket_values[1.0] == 5    # Previous plus 0.75
        assert bucket_values[5.0] == 5    # No change 