"""Tests for the crawler metrics module."""

import pytest
from prometheus_client import REGISTRY
from src.analytics.metrics.crawler_metrics import CrawlerMetrics

@pytest.fixture
def clear_registry():
    """Clear the Prometheus registry before and after each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    yield
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)

@pytest.fixture
def metrics(clear_registry):
    """Get a fresh CrawlerMetrics instance."""
    CrawlerMetrics.reset()
    return CrawlerMetrics()

@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that multiple instances refer to the same object."""
    metrics1 = CrawlerMetrics()
    metrics2 = CrawlerMetrics()
    assert metrics1 is metrics2

@pytest.mark.asyncio
async def test_track_request_basic(metrics):
    """Test basic request tracking."""
    await metrics.track_request(source="github", endpoint="repos")
    
    # Check request counter
    requests = metrics.requests_total.labels(source="github", endpoint="repos", status="success")
    assert requests._value.get() == 1

@pytest.mark.asyncio
async def test_track_request_with_all_metrics(metrics):
    """Test request tracking with all optional metrics."""
    await metrics.track_request(
        source="github",
        endpoint="repos",
        duration=1.5,
        response_size=2000
    )
    
    # Check duration
    duration = metrics.request_duration.labels(source="github", endpoint="repos")
    samples = list(duration._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 1.5
    
    # Check response size
    resp_size = metrics.response_size.labels(source="github", endpoint="repos")
    samples = list(resp_size._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 2000

@pytest.mark.asyncio
async def test_track_error(metrics):
    """Test error tracking."""
    await metrics.track_error(
        source="github",
        endpoint="repos",
        error_type="rate_limit"
    )
    
    errors = metrics.errors_total.labels(
        source="github",
        endpoint="repos",
        error_type="rate_limit"
    )
    assert errors._value.get() == 1

@pytest.mark.asyncio
async def test_active_requests_tracking(metrics):
    """Test active requests tracking."""
    await metrics.start_request(source="github", endpoint="repos")
    active = metrics.active_requests.labels(source="github", endpoint="repos")
    assert active._value.get() == 1
    
    await metrics.end_request(source="github", endpoint="repos")
    assert active._value.get() == 0

@pytest.mark.asyncio
async def test_rate_limit_tracking(metrics):
    """Test rate limit tracking."""
    await metrics.set_rate_limit(source="github", remaining=4000)
    rate_limit = metrics.rate_limit_remaining.labels(source="github")
    assert rate_limit._value.get() == 4000

@pytest.mark.asyncio
async def test_multiple_sources(metrics):
    """Test tracking for multiple sources."""
    # Track GitHub requests
    await metrics.track_request(source="github", endpoint="repos")
    await metrics.track_request(source="github", endpoint="users")
    
    # Track GitLab requests
    await metrics.track_request(source="gitlab", endpoint="projects")
    
    # Check GitHub metrics
    github_repos = metrics.requests_total.labels(source="github", endpoint="repos", status="success")
    github_users = metrics.requests_total.labels(source="github", endpoint="users", status="success")
    assert github_repos._value.get() == 1
    assert github_users._value.get() == 1
    
    # Check GitLab metrics
    gitlab_projects = metrics.requests_total.labels(source="gitlab", endpoint="projects", status="success")
    assert gitlab_projects._value.get() == 1 