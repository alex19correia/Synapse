# Sistema LLM

## Visão Geral
O sistema LLM (Large Language Model) é responsável por gerenciar as interações com modelos de linguagem, especificamente o DeepSeek. O sistema inclui funcionalidades de cache, métricas, retry e processamento de texto.

## Arquitetura

### Componentes Principais

```python
COMPONENTS = {
    "DeepSeekClient": {
        "description": "Cliente principal para interação com a API do DeepSeek",
        "features": [
            "Geração de texto",
            "Streaming de respostas",
            "Cache com Redis",
            "Retry com backoff exponencial",
            "Métricas detalhadas"
        ]
    },
    "LLMMetrics": {
        "description": "Coletor de métricas para operações do LLM",
        "metrics": {
            "counters": [
                "requests_total",
                "tokens_total", 
                "cache_operations"
            ],
            "histograms": [
                "latency",
                "response_length"
            ],
            "gauges": [
                "active_requests"
            ]
        }
    }
}
```

### Funcionalidades Especializadas

```python
SPECIALIZED_FEATURES = {
    "summarize": {
        "description": "Geração de resumos de texto",
        "max_length": "Configurável",
        "cache": "Habilitado"
    },
    "extract_entities": {
        "description": "Extração de entidades nomeadas",
        "entities": ["pessoa", "organização", "local", "data"],
        "formato": "JSON estruturado"
    }
}
```

## Cache e Performance

### Configuração Redis
```python
REDIS_CONFIG = {
    "ttl": 3600,  # 1 hora
    "key_format": "deepseek:response:{hash}",
    "serialization": "JSON"
}
```

### Retry Strategy
```python
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff": "exponential",
    "base_delay": 1,  # segundo
}
```

## Monitoramento

### Métricas Prometheus
- `llm_requests_total`: Total de requisições por operação e status
- `llm_tokens_total`: Total de tokens processados por operação
- `llm_cache_operations_total`: Operações de cache (hits/misses)
- `llm_latency_seconds`: Latência das operações
- `llm_response_length`: Tamanho das respostas
- `llm_active_requests`: Requisições ativas

### Alertas Recomendados
```python
ALERTS = {
    "high_latency": {
        "metric": "llm_latency_seconds",
        "threshold": 5,  # segundos
        "duration": "5m"
    },
    "high_error_rate": {
        "metric": "llm_requests_total{status='error'}",
        "threshold": "10%",
        "duration": "5m"
    },
    "low_cache_hit_rate": {
        "metric": "llm_cache_operations_total{hit='hit'} / llm_cache_operations_total",
        "threshold": "50%",
        "duration": "1h"
    }
}
```

## Exemplos de Uso

### Geração Básica
```python
client = DeepSeekClient()
messages = [
    DeepSeekMessage(role="user", content="Olá!")
]
response = await client.generate_with_cache(messages)
```

### Streaming
```python
async for token in client.stream_generate(messages):
    print(token, end="")
```

### Resumo
```python
summary = await client.summarize(text, max_length=100)
```

### Extração de Entidades
```python
entities = await client.extract_entities(text)
```

## Próximos Passos

1. Implementar validação de saída com JSON Schema
2. Adicionar suporte a outros modelos além do DeepSeek
3. Implementar rate limiting por usuário
4. Expandir métricas de negócio
5. Adicionar testes de carga 