# Synapse Testing Documentation 📚

## Overview
This document provides a comprehensive guide to the testing infrastructure of the Synapse project.

## Test Categories

### 1. Unit Tests
- Component-level testing
- Isolated functionality
- Mock dependencies
- Fast execution

### 2. Integration Tests
- Component interaction
- Real dependencies
- System behavior
- End-to-end flows

### 3. Performance Tests
- Response time
- Resource usage
- Concurrent load
- System stability

## Test Coverage

### Core Components
- ✅ API System
- ✅ LLM Integration
- ✅ Cache System
- ✅ Crawler System
- ✅ RAG System

### Performance Metrics
- Response Time: < 1.0s
- Memory Usage: < 100MB
- Success Rate: > 95%
- Reliability: > 99%

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
# All tests
pytest tests/

# Specific categories
pytest tests/api/
pytest tests/llm/
pytest tests/cache/
pytest tests/crawler/
pytest tests/rag/
pytest tests/e2e/
pytest tests/performance/

# With coverage
pytest --cov=src/ tests/
```

## Test Documentation
- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [E2E Tests](e2e-tests.md)
- [Performance Tests](performance-tests.md)

## Best Practices
1. Write clear test descriptions
2. Follow AAA pattern (Arrange, Act, Assert)
3. Use appropriate fixtures
4. Clean up resources
5. Handle errors gracefully

## Coverage Requirements
- Lines: 90%
- Branches: 85%
- Functions: 95%
- Critical paths: 100% 