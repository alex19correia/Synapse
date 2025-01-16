# Sistema de Analytics

## Visão Geral
O sistema de analytics é responsável por coletar, processar e analisar métricas de diferentes componentes da aplicação, incluindo LLM, crawlers e infraestrutura.

## Arquitetura

### Componentes

```python
ANALYTICS_COMPONENTS = {
    "LLM": {
        "metrics": {
            "requests": {
                "type": "counter",
                "labels": ["operation", "status"]
            },
            "tokens": {
                "type": "counter",
                "labels": ["operation"]
            },
            "latency": {
                "type": "histogram",
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0]
            },
            "cache": {
                "type": "counter",
                "labels": ["operation", "status"]
            }
        }
    },
    "Crawler": {
        "metrics": {
            "pages": {
                "type": "counter",
                "labels": ["status"]
            },
            "duration": {
                "type": "histogram",
                "buckets": [1.0, 5.0, 10.0, 30.0, 60.0]
            },
            "errors": {
                "type": "counter",
                "labels": ["type"]
            },
            "batch": {
                "type": "gauge",
                "labels": ["stage"]
            }
        }
    }
}
```

### Processamento

```python
PROCESSING_CONFIG = {
    "batch": {
        "size": 100,
        "interval": "10s",
        "retry": {
            "attempts": 3,
            "backoff": "exponential"
        }
    },
    "validation": {
        "schema": True,
        "types": True,
        "required": ["timestamp", "component"]
    },
    "enrichment": {
        "add_metadata": True,
        "normalize": True
    }
}
```

### Armazenamento

```python
STORAGE_CONFIG = {
    "prometheus": {
        "retention": "15d",
        "scrape_interval": "10s",
        "evaluation_interval": "1m"
    },
    "redis": {
        "ttl": 3600,
        "max_memory": "1gb",
        "eviction": "volatile-lru"
    }
}
```

## Métricas

### LLM

```python
LLM_METRICS = {
    "performance": {
        "requests_total": {
            "type": "counter",
            "description": "Total de requisições ao LLM"
        },
        "tokens_total": {
            "type": "counter",
            "description": "Total de tokens processados"
        },
        "latency_seconds": {
            "type": "histogram",
            "description": "Latência das requisições"
        }
    },
    "cache": {
        "hits_total": {
            "type": "counter",
            "description": "Cache hits"
        },
        "misses_total": {
            "type": "counter",
            "description": "Cache misses"
        },
        "size_bytes": {
            "type": "gauge",
            "description": "Tamanho do cache"
        }
    },
    "errors": {
        "total": {
            "type": "counter",
            "description": "Total de erros"
        },
        "by_type": {
            "type": "counter",
            "labels": ["error_type"],
            "description": "Erros por tipo"
        }
    }
}
```

### Crawler

```python
CRAWLER_METRICS = {
    "performance": {
        "pages_total": {
            "type": "counter",
            "description": "Total de páginas crawleadas"
        },
        "duration_seconds": {
            "type": "histogram",
            "description": "Duração do crawling"
        },
        "batch_size": {
            "type": "gauge",
            "description": "Tamanho do batch atual"
        }
    },
    "errors": {
        "total": {
            "type": "counter",
            "description": "Total de erros"
        },
        "by_type": {
            "type": "counter",
            "labels": ["error_type"],
            "description": "Erros por tipo"
        }
    },
    "rate_limiting": {
        "requests": {
            "type": "gauge",
            "description": "Requisições por minuto"
        },
        "limit": {
            "type": "gauge",
            "description": "Limite atual"
        }
    }
}
```

## Alertas

### Configuração

```python
ALERT_CONFIG = {
    "rules": {
        "high_error_rate": {
            "condition": "rate(errors_total[5m]) > 0.1",
            "severity": "critical",
            "channels": ["slack", "email"]
        },
        "slow_processing": {
            "condition": "rate(duration_seconds_sum[5m]) / rate(duration_seconds_count[5m]) > 30",
            "severity": "warning",
            "channels": ["slack"]
        },
        "cache_issues": {
            "condition": "rate(cache_misses_total[5m]) / rate(cache_hits_total[5m]) > 0.5",
            "severity": "warning",
            "channels": ["slack"]
        }
    }
}
```

## Próximos Passos

1. Implementar métricas de negócio
2. Adicionar visualizações customizadas
3. Melhorar alertas
4. Configurar retenção de dados
5. Otimizar processamento em batch 