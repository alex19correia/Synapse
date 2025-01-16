"""Tests for the LLM metrics module."""

import pytest
from prometheus_client import REGISTRY
from src.analytics.metrics.llm_metrics import LLMMetrics

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
    """Get a fresh LLMMetrics instance."""
    LLMMetrics.reset()
    return LLMMetrics()

@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that multiple instances refer to the same object."""
    metrics1 = LLMMetrics()
    metrics2 = LLMMetrics()
    assert metrics1 is metrics2

@pytest.mark.asyncio
async def test_track_request_basic(metrics):
    """Test basic request tracking."""
    await metrics.track_request(
        model="test-model",
        endpoint="completion"
    )
    
    # Check request counter
    requests = metrics.requests_total.labels(
        model="test-model",
        endpoint="completion",
        status="success"
    )
    assert requests._value.get() == 1

@pytest.mark.asyncio
async def test_track_request_with_all_metrics(metrics):
    """Test request tracking with all optional metrics."""
    await metrics.track_request(
        model="test-model",
        endpoint="completion",
        status="success",
        duration=1.5,
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        response_length=500
    )
    
    # Check duration
    duration = metrics.request_duration.labels(model="test-model", endpoint="completion")
    samples = list(duration._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 1.5
    
    # Check prompt tokens
    prompt_tokens = metrics.token_counts.labels(model="test-model", endpoint="completion", token_type="prompt")
    samples = list(prompt_tokens._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 100
    
    # Check completion tokens
    completion_tokens = metrics.token_counts.labels(model="test-model", endpoint="completion", token_type="completion")
    samples = list(completion_tokens._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 50
    
    # Check total tokens
    total_tokens = metrics.token_counts.labels(model="test-model", endpoint="completion", token_type="total")
    samples = list(total_tokens._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 150
    
    # Check response length
    length = metrics.response_length.labels(model="test-model", endpoint="completion")
    samples = list(length._samples())
    count_sample = next(s for s in samples if s.name.endswith('_count'))
    sum_sample = next(s for s in samples if s.name.endswith('_sum'))
    assert count_sample.value == 1
    assert sum_sample.value == 500

@pytest.mark.asyncio
async def test_track_error(metrics):
    """Test error tracking."""
    await metrics.track_error(
        model="test-model",
        endpoint="completion",
        error_type="rate_limit"
    )
    
    errors = metrics.errors_total.labels(
        model="test-model",
        endpoint="completion",
        error_type="rate_limit"
    )
    assert errors._value.get() == 1

@pytest.mark.asyncio
async def test_active_requests_tracking(metrics):
    """Test active requests tracking."""
    await metrics.start_request(model="test-model", endpoint="completion")
    active = metrics.active_requests.labels(model="test-model", endpoint="completion")
    assert active._value.get() == 1
    
    await metrics.end_request(model="test-model", endpoint="completion")
    assert active._value.get() == 0

@pytest.mark.asyncio
async def test_rate_limit_tracking(metrics):
    """Test rate limit tracking."""
    await metrics.set_rate_limit(model="test-model", remaining=4000)
    rate_limit = metrics.rate_limit_remaining.labels(model="test-model")
    assert rate_limit._value.get() == 4000

@pytest.mark.asyncio
async def test_multiple_models(metrics):
    """Test tracking for multiple models."""
    # Track requests for different models
    await metrics.track_request(model="gpt-4", endpoint="completion")
    await metrics.track_request(model="gpt-3.5", endpoint="completion")
    await metrics.track_request(model="claude-3", endpoint="chat")
    
    # Check metrics for each model
    gpt4 = metrics.requests_total.labels(model="gpt-4", endpoint="completion", status="success")
    gpt35 = metrics.requests_total.labels(model="gpt-3.5", endpoint="completion", status="success")
    claude = metrics.requests_total.labels(model="claude-3", endpoint="chat", status="success")
    
    assert gpt4._value.get() == 1
    assert gpt35._value.get() == 1
    assert claude._value.get() == 1 