# End-to-End Testing Documentation

## Overview
The end-to-end tests ensure that all components of the Synapse API work together correctly. The tests cover various aspects of the system including chat completion, RAG integration, authentication, rate limiting, and security features.

## Test Structure
Tests are organized in the `tests/e2e/test_synapse_e2e.py` file and use pytest with asyncio support. The main test class `TestSynapseE2E` contains the following test categories:

### 1. Basic Functionality Tests
- `test_basic_chat_flow`: Verifies basic chat completion functionality
- `test_streaming_chat_flow`: Tests streaming responses
- `test_rag_enhanced_chat`: Validates RAG context integration

### 2. Error Handling and Security Tests
- `test_error_handling`: Validates error responses for invalid inputs
- `test_security_headers`: Ensures proper security headers are set
- `test_input_validation`: Checks input sanitization and validation
- `test_rate_limiting`: Verifies rate limiting functionality

### 3. Integration Tests
- `test_document_management`: Tests document indexing and retrieval
- `test_conversation_memory`: Validates context maintenance
- `test_system_integration`: Tests full system integration
- `test_authentication_flow`: Verifies auth workflow
- `test_performance_requirements`: Checks performance metrics

## Test Environment
The test environment is configured to:
- Use mock responses in test mode
- Skip rate limiting for most endpoints except specific test cases
- Apply stricter rate limits (5 requests/second) for rate limiting tests
- Use test-specific headers to identify rate limit tests

## Rate Limiting Implementation
Rate limiting in tests is controlled through:
1. Test headers (`test-name`) to identify rate limit tests
2. Separate rate limiting logic for test environment
3. Configurable limits based on environment

## Security Headers
The following security headers are enforced:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## Running Tests
To run the E2E tests:
```bash
pytest tests/e2e/test_synapse_e2e.py -v
```

## Test Dependencies
- pytest
- pytest-asyncio
- httpx
- FastAPI TestClient

## Future Improvements
1. Address Pydantic deprecation warnings by migrating to ConfigDict
2. Improve HTTPX content handling in tests
3. Add more comprehensive performance testing
4. Implement proper database mocking 