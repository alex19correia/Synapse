import pytest
from prometheus_client import REGISTRY
from src.analytics.metrics.api_metrics import APIMetrics

@pytest.fixture
def metrics():
    """Fixture for API metrics with clean registry."""
    # Clear registry before each test
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    
    return APIMetrics()

@pytest.mark.asyncio
class TestAPIMetrics:
    async def test_singleton_pattern(self):
        """Tests that APIMetrics follows singleton pattern."""
        metrics1 = APIMetrics()
        metrics2 = APIMetrics()
        assert metrics1 is metrics2
    
    async def test_track_request_basic(self, metrics):
        """Tests basic request tracking."""
        await metrics.track_request(
            method="GET",
            endpoint="/api/v1/test"
        )
        
        # Verify counter was incremented
        value = metrics.requests_total.labels(
            method="GET",
            endpoint="/api/v1/test",
            status="success"
        )._value.get()
        assert value == 1
    
    async def test_track_request_with_all_metrics(self, metrics):
        """Tests request tracking with all optional metrics."""
        # Clear any existing metrics
        metrics.requests_total._metrics.clear()
        metrics.request_duration._metrics.clear()
        metrics.request_size._metrics.clear()
        metrics.response_size._metrics.clear()

        await metrics.track_request(
            method="POST",
            endpoint="/api/v1/test",
            status="success",
            duration=1.5,
            request_size=1000,
            response_size=2000
        )
        
        # Verify all metrics were recorded
        assert metrics.requests_total.labels(
            method="POST",
            endpoint="/api/v1/test",
            status="success"
        )._value.get() == 1
        
        # Check duration histogram
        duration = metrics.request_duration.labels(
            method="POST",
            endpoint="/api/v1/test"
        )
        assert duration._value.get_sample_count() == 1
        assert duration._value.get_sample_sum() == 1.5
        
        # Check request size histogram
        req_size = metrics.request_size.labels(
            method="POST",
            endpoint="/api/v1/test"
        )
        assert req_size._value.get_sample_count() == 1
        assert req_size._value.get_sample_sum() == 1000
        
        # Check response size histogram
        resp_size = metrics.response_size.labels(
            method="POST",
            endpoint="/api/v1/test"
        )
        assert resp_size._value.get_sample_count() == 1
        assert resp_size._value.get_sample_sum() == 2000
    
    async def test_track_error(self, metrics):
        """Tests error tracking."""
        await metrics.track_error(
            method="GET",
            endpoint="/api/v1/test",
            error_type="validation_error"
        )
        
        value = metrics.errors_total.labels(
            method="GET",
            endpoint="/api/v1/test",
            error_type="validation_error"
        )._value.get()
        assert value == 1
    
    async def test_active_requests_tracking(self, metrics):
        """Tests active requests gauge."""
        # Start multiple requests
        await metrics.start_request(
            method="GET",
            endpoint="/api/v1/test"
        )
        await metrics.start_request(
            method="POST",
            endpoint="/api/v1/test"
        )
        
        value = metrics.active_requests.labels(
            method="GET",
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 1
        
        value = metrics.active_requests.labels(
            method="POST",
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 1
        
        # End requests
        await metrics.end_request(
            method="GET",
            endpoint="/api/v1/test"
        )
        await metrics.end_request(
            method="POST",
            endpoint="/api/v1/test"
        )
        
        value = metrics.active_requests.labels(
            method="GET",
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 0
        
        value = metrics.active_requests.labels(
            method="POST",
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 0
    
    async def test_rate_limit_tracking(self, metrics):
        """Tests rate limit tracking."""
        # Set rate limit
        await metrics.set_rate_limit(
            endpoint="/api/v1/test",
            remaining=100
        )
        
        value = metrics.rate_limit_remaining.labels(
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 100
        
        # Update rate limit
        await metrics.set_rate_limit(
            endpoint="/api/v1/test",
            remaining=99
        )
        
        value = metrics.rate_limit_remaining.labels(
            endpoint="/api/v1/test"
        )._value.get()
        assert value == 99
    
    async def test_multiple_endpoints(self, metrics):
        """Tests tracking multiple different endpoints."""
        endpoints = ["/api/v1/test1", "/api/v1/test2", "/api/v1/test3"]
        methods = ["GET", "POST", "PUT"]
        
        for endpoint in endpoints:
            for method in methods:
                await metrics.track_request(method=method, endpoint=endpoint)
                await metrics.track_error(method=method, endpoint=endpoint, error_type="test_error")
                await metrics.set_rate_limit(endpoint=endpoint, remaining=100)
        
        # Verify each endpoint was tracked
        for endpoint in endpoints:
            for method in methods:
                req_value = metrics.requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status="success"
                )._value.get()
                assert req_value == 1
                
                err_value = metrics.errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type="test_error"
                )._value.get()
                assert err_value == 1
                
                rate_value = metrics.rate_limit_remaining.labels(
                    endpoint=endpoint
                )._value.get()
                assert rate_value == 100 