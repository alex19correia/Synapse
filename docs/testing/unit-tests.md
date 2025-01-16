# Unit Tests 🧪

## Overview
Unit tests validate individual components of the system, ensuring each unit functions as expected.

## Structure

### 1. Organization
```
tests/
├── api/                # API tests
│   └── test_routes.py # Route tests
├── llm/               # LLM tests
│   └── test_deepseek_client.py # DeepSeek client tests
├── cache/             # Cache tests
│   └── test_cache_system.py # Redis cache tests
├── crawler/           # Crawler tests
│   └── test_crawler_system.py # Web crawler tests
└── rag/              # RAG tests
    └── test_rag_system.py # RAG system tests
```

## Implemented Tests

### 1. API Tests
- Route handlers
- Middleware functions
- Authentication
- Rate limiting
- Error handling
- Request validation

### 2. LLM Tests
- Basic chat completion
- Streaming responses
- Error recovery
- Rate limit handling
- Context management
- Model parameters

### 3. Cache Tests
- Basic operations (set/get)
- TTL management
- Complex data handling
- Concurrent operations
- Error handling
- Metrics collection

### 4. Crawler Tests
- Page fetching
- Rate limiting
- HTML parsing
- Metadata extraction
- Robots.txt compliance
- Content filtering

### 5. RAG Tests
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
```

### Execution
```bash
# All tests
pytest tests/

# Specific components
pytest tests/api/
pytest tests/llm/
pytest tests/cache/
pytest tests/crawler/
pytest tests/rag/

# With coverage
pytest --cov=src/ tests/
```

## Best Practices

### 1. Test Structure
- One test file per module
- Clear test names
- Focused test cases
- Proper setup/teardown

### 2. Assertions
- Specific assertions
- Clear error messages
- Complete validation
- Edge case handling

### 3. Mocking
- External services
- Database calls
- File operations
- Network requests

## Coverage Requirements

### Minimum Coverage
- Lines: 90%
- Branches: 85%
- Functions: 95%

### Critical Areas
- Error handling: 100%
- Data validation: 100%
- Core logic: 100%
- API endpoints: 100% 