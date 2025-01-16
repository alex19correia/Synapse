# Integration Tests 🔄

## Overview
Integration tests validate the interaction between different components of the system, ensuring they work correctly together.

## Test Structure

### 1. LLM Integration
Located in `tests/llm/test_deepseek_integration.py`:
- Basic chat completion
- Streaming responses
- Concurrent requests
- Long conversations
- Error recovery
- Rate limit handling
- Model parameters
- Response format
- Context handling
- Error cases

### 2. Cache Integration
Located in `tests/cache/test_cache_system.py`:
- Redis connection
- Basic operations
- TTL management
- Complex data
- Concurrent operations
- Error handling
- Cache invalidation
- Cache metrics
- Bulk operations
- Cache persistence

### 3. Crawler Integration
Located in `tests/crawler/test_crawler_system.py`:
- Page fetching
- Rate limiting
- HTML parsing
- Metadata extraction
- Concurrent crawling
- Error handling
- Robots.txt compliance
- Sitemap parsing
- Content filtering

### 4. RAG Integration
Located in `tests/rag/test_rag_system.py`:
- Document indexing
- Similarity search
- Context retrieval
- Embedding generation
- Cache integration
- Error handling

## Test Requirements

### Performance
- Response time < 1s
- Memory usage < 100MB
- Concurrent operations
- Error recovery
- Rate limiting

### Reliability
- Error handling
- Edge cases
- Resource cleanup
- State management
- Timeout handling

## Running Tests

### Setup
```bash
# Install dependencies
pip install pytest pytest-asyncio pytest-cov

# Set environment
export PYTHONPATH=src/
export TEST_ENV=true

# Start required services
docker compose up -d redis
```

### Execution
```bash
# All integration tests
pytest tests/ -m integration

# Specific components
pytest tests/llm/ -m integration
pytest tests/cache/ -m integration
pytest tests/crawler/ -m integration
pytest tests/rag/ -m integration

# With coverage
pytest --cov=src/ tests/ -m integration
```

## Test Cases

### 1. LLM Integration
```python
@pytest.mark.integration
async def test_chat_completion():
    """Tests basic chat completion."""
    client = DeepSeekClient()
    response = await client.generate([
        {"role": "user", "content": "Hello"}
    ])
    assert response.content is not None
```

### 2. Cache Integration
```python
@pytest.mark.integration
async def test_cache_operations():
    """Tests cache operations."""
    cache = Cache()
    await cache.set("test", "value")
    value = await cache.get("test")
    assert value == "value"
```

### 3. Crawler Integration
```python
@pytest.mark.integration
async def test_page_fetch():
    """Tests page fetching."""
    crawler = Crawler()
    content = await crawler.fetch_page("https://example.com")
    assert content is not None
```

### 4. RAG Integration
```python
@pytest.mark.integration
async def test_document_search():
    """Tests document search."""
    rag = RAGSystem()
    results = await rag.search("test query")
    assert len(results) > 0
```

## Best Practices

### 1. Test Structure
- Clear component separation
- Proper setup/teardown
- Resource management
- Error handling

### 2. Assertions
- Comprehensive checks
- Clear error messages
- State validation
- Performance metrics

### 3. Mocking
- External services
- Rate limits
- Network conditions
- Error scenarios

## Coverage Requirements

### Minimum Coverage
- Lines: 90%
- Branches: 85%
- Functions: 95%

### Critical Areas
- Component interactions: 100%
- Error handling: 100%
- Resource cleanup: 100%
- State management: 100% 