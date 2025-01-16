# Sistema LLM 🤖

## Visão Geral

O sistema LLM (Large Language Model) do Synapse Assistant é responsável pelo processamento de linguagem natural, geração de texto, e integração com modelos de linguagem.

## Componentes

### 1. DeepSeek Client
```python
from src.llm.deepseek_client import DeepSeekClient

client = DeepSeekClient()
response = await client.generate(messages)
```

#### Features
- Geração de texto
- Streaming de respostas
- Cache automático
- Retry com backoff
- Métricas detalhadas
- Extração de entidades
- Sumarização

#### Configuração
```python
settings = {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 1000,
    "cache_ttl": 3600
}
```

### 2. Sistema de Cache

#### Redis Integration
```python
from redis.asyncio import Redis

redis = Redis.from_url(settings.REDIS_URL)
```

#### Cache Key Generation
```python
def get_cache_key(messages, **params):
    data = {
        "messages": messages,
        "params": params
    }
    return f"llm:response:{hash(json.dumps(data))}"
```

#### TTL Management
- Default: 1 hora
- Configurável por operação
- Invalidação automática

### 3. Métricas

#### Prometheus Metrics
- `llm_requests_total`
- `llm_tokens_total`
- `llm_latency_seconds`
- `llm_cache_operations`
- `llm_active_requests`

#### Grafana Dashboards
- Latência
- Cache hits/misses
- Token usage
- Error rates

### 4. RAG Integration

#### Document Processing
```python
from src.rag.processor import RAGProcessor

processor = RAGProcessor()
chunks = await processor.process_document(text)
```

#### Vector Store
- Qdrant para embeddings
- Chunking automático
- Metadata tracking
- Similarity search

## Fluxos de Uso

### 1. Geração Básica
```python
messages = [
    DeepSeekMessage(role="user", content="Query")
]
response = await client.generate(messages)
```

### 2. Streaming
```python
async for token in client.stream_generate(messages):
    yield token
```

### 3. RAG
```python
# Index document
await processor.add_document(text)

# Query
results = await processor.query(question)
```

## Error Handling

### Retry Logic
```python
async def generate_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await generate(messages)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)
```

### Error Types
- API Errors
- Rate Limits
- Timeout
- Invalid Input
- Cache Errors

## Performance

### Otimizações
1. Cache em memória
2. Connection pooling
3. Batch processing
4. Async operations
5. Request coalescing

### Limites
- Rate limits
- Token limits
- Concurrent requests
- Cache size
- Request timeout

## Monitoramento

### Métricas Chave
1. Latência (p50, p95, p99)
2. Cache hit ratio
3. Error rate
4. Token usage
5. Request volume

### Alertas
- High latency
- Error spikes
- Cache misses
- Rate limiting
- Token usage

## Segurança

### Proteções
1. Input validation
2. Output sanitization
3. Rate limiting
4. Authentication
5. Encryption

### Dados Sensíveis
- API keys
- User data
- Cache data
- Logs

## Manutenção

### Rotinas
- Cache cleanup
- Log rotation
- Metric aggregation
- Performance tuning
- Security updates

### Deployment
- Canary releases
- Feature flags
- A/B testing
- Rollback procedures

## Troubleshooting

### Common Issues
1. High latency
   - Check cache hit ratio
   - Monitor API response times
   - Verify connection pooling

2. Cache misses
   - Validate cache keys
   - Check TTL settings
   - Monitor eviction rate

3. Error spikes
   - Check API status
   - Verify rate limits
   - Monitor system resources

## Referências

- [DeepSeek API Docs](https://deepseek.com/docs)
- [Redis Documentation](https://redis.io/docs)
- [Qdrant Docs](https://qdrant.tech/docs)
- [FastAPI AsyncIO](https://fastapi.tiangolo.com/async/) 