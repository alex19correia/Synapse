# Sistema de API 🌐

## Visão Geral

O sistema de API do Synapse Assistant fornece uma interface RESTful para interação com todos os componentes do sistema, incluindo geração de texto, processamento de documentos e análise de dados.

## Endpoints

### 1. LLM Endpoints

#### Generate Text
```http
POST /api/v1/llm/generate
Content-Type: application/json

{
    "messages": [
        {
            "role": "user",
            "content": "Query text"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}
```

#### Stream Generate
```http
POST /api/v1/llm/stream
Content-Type: application/json

{
    "messages": [
        {
            "role": "user",
            "content": "Query text"
        }
    ]
}
```

#### Summarize
```http
POST /api/v1/llm/summarize
Content-Type: application/json

{
    "text": "Long text to summarize",
    "max_length": 200
}
```

### 2. RAG Endpoints

#### Process Document
```http
POST /api/v1/rag/process
Content-Type: application/json

{
    "text": "Document content",
    "metadata": {
        "source": "url",
        "type": "article"
    }
}
```

#### Query
```http
POST /api/v1/rag/query
Content-Type: application/json

{
    "question": "User question",
    "filters": {
        "source": "url"
    }
}
```

### 3. Analytics Endpoints

#### Get Metrics
```http
GET /api/v1/metrics
Accept: application/json
```

#### Track Event
```http
POST /api/v1/analytics/event
Content-Type: application/json

{
    "event_type": "user_action",
    "data": {
        "action": "query",
        "duration": 0.5
    }
}
```

## Middleware

### 1. Authentication
```python
from fastapi import Depends, HTTPException
from src.auth import verify_token

async def auth_middleware(token: str):
    if not verify_token(token):
        raise HTTPException(status_code=401)
    return token
```

### 2. Rate Limiting
```python
from src.middleware import RateLimiter

limiter = RateLimiter(
    requests_per_minute=60,
    burst_size=10
)
```

### 3. Error Handling
```python
from fastapi import HTTPException
from src.middleware import handle_errors

@handle_errors
async def protected_route():
    # Route logic here
    pass
```

## Validação

### 1. Request Models
```python
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    messages: list[Message]
    temperature: float = Field(0.7, ge=0, le=1)
    max_tokens: int = Field(1000, gt=0)
```

### 2. Response Models
```python
class GenerateResponse(BaseModel):
    content: str
    usage: TokenUsage
    finish_reason: str
```

## Segurança

### 1. Authentication
- API Key validation
- JWT tokens
- Role-based access
- Rate limiting per key

### 2. Data Protection
- Input sanitization
- Output validation
- HTTPS only
- Data encryption

## Performance

### 1. Caching
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def setup_cache():
    FastAPICache.init(RedisBackend())
```

### 2. Optimizations
- Connection pooling
- Response compression
- Async operations
- Request batching

## Monitoramento

### 1. Logging
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info("request_started",
                method=request.method,
                path=request.url.path)
```

### 2. Métricas
- Request count
- Response time
- Error rates
- Cache stats
- Resource usage

## Documentação

### 1. OpenAPI Spec
```yaml
openapi: 3.0.0
info:
  title: Synapse API
  version: 1.0.0
paths:
  /api/v1/llm/generate:
    post:
      summary: Generate text
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GenerateRequest'
```

### 2. API Docs
- Swagger UI
- ReDoc
- Postman collection
- Code examples

## Error Handling

### 1. HTTP Errors
```python
class APIError(HTTPException):
    def __init__(self, code: int, message: str):
        super().__init__(
            status_code=code,
            detail={"message": message}
        )
```

### 2. Error Types
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Error

## Testing

### 1. Unit Tests
```python
async def test_generate_endpoint():
    response = await client.post(
        "/api/v1/llm/generate",
        json={"messages": [{"role": "user", "content": "test"}]}
    )
    assert response.status_code == 200
```

### 2. Integration Tests
```python
async def test_full_flow():
    # Process document
    doc_response = await process_document()
    
    # Query document
    query_response = await query_document()
    
    assert query_response.status_code == 200
```

## Deployment

### 1. Configuration
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    redis_url: str
    model_name: str
```

### 2. Environment
- Development
- Staging
- Production
- Testing

## Manutenção

### 1. Health Checks
```http
GET /health
Response: 200 OK

{
    "status": "healthy",
    "version": "1.0.0",
    "dependencies": {
        "database": "up",
        "cache": "up",
        "llm": "up"
    }
}
```

### 2. Versioning
- Semantic versioning
- API versioning
- Database migrations
- Dependency updates

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/) 