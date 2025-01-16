# End-to-End Tests 🌐

## Overview
End-to-end tests validate the complete system flow, ensuring all components work together correctly.

## Test Structure

### 1. Basic Flows
Located in `tests/e2e/test_synapse_e2e.py`:
- Basic chat completion
- Streaming chat
- RAG-enhanced chat
- Error handling
- Document management
- Conversation memory
- System integration
- Performance requirements

### 2. Performance Tests
Located in `tests/performance/test_performance.py`:
- Chat completion latency
- Concurrent load
- RAG performance
- Memory usage
- Stress testing
- Cache performance
- Long-running stability

## Test Requirements

### Performance
- Average response time: < 1.0s
- 95th percentile: < 2.0s
- 99th percentile: < 3.0s
- Memory increase: < 100MB
- Success rate: > 95%
- Timeouts: < 5 per 100 requests

### Reliability
- Long-term stability: > 99%
- Error handling
- Resource cleanup
- State management
- Cache performance

## Test Cases

### 1. Basic Chat Flow
```python
async def test_basic_chat_flow(async_client):
    """Tests basic chat completion flow."""
    response = await async_client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "What is 2+2?"}
            ],
            "model": "deepseek-chat"
        }
    )
    assert response.status_code == 200
    assert "choices" in response.json()
```

### 2. RAG Integration
```python
async def test_rag_enhanced_chat(async_client):
    """Tests chat completion with RAG context."""
    # Index document
    await async_client.post(
        "/v1/documents/index",
        json={
            "content": "Test content",
            "metadata": {"source": "test"}
        }
    )
    
    # Test RAG-enhanced chat
    response = await async_client.post(
        "/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Test query"}],
            "use_rag": True
        }
    )
    assert response.status_code == 200
```

### 3. Performance Testing
```python
async def test_performance_requirements(async_client):
    """Tests system performance requirements."""
    start_time = time.time()
    response = await async_client.post(
        "/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Test"}]
        }
    )
    end_time = time.time()
    assert end_time - start_time < 5  # Response within 5 seconds
```

## Running Tests

### Setup
```bash
# Install dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Set environment
export PYTHONPATH=src/
export TEST_ENV=true

# Start services
docker compose up -d
```

### Execution
```bash
# All E2E tests
pytest tests/e2e/

# Performance tests
pytest tests/performance/

# With coverage
pytest --cov=src/ tests/e2e/
```

## Best Practices

### 1. Test Structure
- Complete flows
- Realistic scenarios
- Error handling
- Performance monitoring

### 2. Assertions
- Response validation
- State verification
- Performance metrics
- Error conditions

### 3. Environment
- Isolated testing
- Clean state
- Resource management
- Service dependencies

## Coverage Requirements

### Minimum Coverage
- Lines: 90%
- Branches: 85%
- Functions: 95%

### Critical Areas
- User flows: 100%
- Error handling: 100%
- Performance metrics: 100%
- Data persistence: 100%

## Monitoring

### 1. Metrics
- Response times
- Success rates
- Error rates
- Resource usage

### 2. Logging
- Request/response
- Error details
- Performance data
- System state 