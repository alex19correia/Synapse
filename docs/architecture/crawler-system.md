# Sistema de Crawling

Sistema de crawling baseado em Crawl4AI, otimizado para extração paralela de conteúdo e integração com RAG.

## Arquitetura

### Componentes Principais

```python
crawler_components = {
    "ParallelCrawler": {
        "description": "Motor principal de crawling",
        "features": [
            "Processamento paralelo de URLs",
            "Integração com RAG",
            "Cache distribuído",
            "Rate limiting"
        ]
    },
    "RateLimiter": {
        "description": "Controle de taxa de requisições",
        "config": {
            "requests_per_second": 5,
            "max_requests_per_domain": 10,
            "cooldown_period": 30
        }
    },
    "DistributedCache": {
        "description": "Cache Redis para conteúdo",
        "config": {
            "enabled": True,
            "ttl": 3600,
            "max_size": "1GB"
        }
    }
}
```

### Integração RAG

```python
rag_pipeline = {
    "extração": {
        "chunking": "Divisão semântica do conteúdo",
        "embeddings": "Geração de embeddings por chunk",
        "storage": "Armazenamento em vector store"
    },
    "processamento": {
        "batch_size": 10,
        "max_tokens": 512,
        "overlap": 50
    }
}
```

### Monitoramento

```python
monitoring = {
    "métricas": {
        "crawl": [
            "URLs processadas",
            "Taxa de sucesso",
            "Erros",
            "Tempo de processamento"
        ],
        "cache": [
            "Hit rate",
            "Tamanho",
            "Invalidações"
        ],
        "rate_limit": [
            "Requisições/segundo",
            "Bloqueios por domínio",
            "Períodos de cooldown"
        ]
    },
    "alertas": [
        "Taxa de erro > 10%",
        "Cache próximo do limite",
        "Rate limit excedido"
    ]
}
```

## Configuração

```python
config = {
    "browser": {
        "headless": True,
        "timeout": 30000,
        "persistent": False
    },
    "extraction": {
        "use_llm": False,
        "max_retries": 3,
        "retry_delay": 1000
    },
    "rate_limit": {
        "requests_per_second": 5,
        "max_requests_per_domain": 10,
        "cooldown_period": 30
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,
        "max_size": "1GB"
    }
}
```

## Fluxo de Dados

1. Input: URLs e configurações
2. Rate limiting: Verifica limites
3. Cache: Busca conteúdo em cache
4. Crawling: Extrai conteúdo em paralelo
5. Processamento RAG: Chunks e embeddings
6. Output: Conteúdo estruturado e métricas

## Integração com Sistemas

- RAG: Processamento de conteúdo para knowledge base
- Métricas: Prometheus para monitoramento
- Logging: Estruturado com níveis e contexto
- Cache: Redis para armazenamento distribuído

## Próximos Passos

1. Otimizar paralelismo com base em métricas
2. Adicionar validações de conteúdo
3. Implementar retry com backoff exponencial
4. Expandir testes de integração

## Referências

- [Crawl4AI](https://github.com/crawl4ai)
- [Playwright](https://playwright.dev)
- [RAG](docs/architecture/rag-system.md) 