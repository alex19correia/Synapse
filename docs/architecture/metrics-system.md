# Sistema de Métricas

## Visão Geral
O sistema de métricas é responsável por coletar, processar e expor métricas de diferentes componentes da aplicação, incluindo LLM, crawlers e infraestrutura.

## Arquitetura

### Componentes

```python
METRICS_COMPONENTS = {
    "LLM": {
        "counters": {
            "requests_total": {
                "labels": ["operation", "status"],
                "help": "Total de requisições ao LLM"
            },
            "tokens_total": {
                "labels": ["operation"],
                "help": "Total de tokens processados"
            },
            "errors_total": {
                "labels": ["type"],
                "help": "Total de erros"
            }
        },
        "histograms": {
            "latency_seconds": {
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0],
                "help": "Latência das requisições"
            },
            "tokens_per_request": {
                "buckets": [100, 500, 1000, 2000, 5000],
                "help": "Tokens por requisição"
            }
        },
        "gauges": {
            "active_requests": {
                "help": "Requisições ativas"
            },
            "cache_size_bytes": {
                "help": "Tamanho do cache"
            }
        }
    },
    "Crawler": {
        "counters": {
            "pages_total": {
                "labels": ["status"],
                "help": "Total de páginas crawleadas"
            },
            "errors_total": {
                "labels": ["type"],
                "help": "Total de erros"
            }
        },
        "histograms": {
            "duration_seconds": {
                "buckets": [1.0, 5.0, 10.0, 30.0, 60.0],
                "help": "Duração do crawling"
            },
            "content_size_bytes": {
                "buckets": [1000, 10000, 100000, 1000000],
                "help": "Tamanho do conteúdo"
            }
        },
        "gauges": {
            "active_crawls": {
                "help": "Crawls ativos"
            },
            "batch_size": {
                "help": "Tamanho do batch atual"
            },
            "queue_size": {
                "help": "Tamanho da fila"
            }
        }
    }
}
```

### Coleta

```python
COLLECTION_CONFIG = {
    "prometheus": {
        "port": 9090,
        "path": "/metrics",
        "scrape_interval": "10s",
        "evaluation_interval": "1m"
    },
    "exporters": {
        "python": {
            "type": "prometheus_client",
            "port": 8000,
            "path": "/metrics"
        },
        "node": {
            "type": "prom-client",
            "port": 3000,
            "path": "/metrics"
        }
    }
}
```

### Processamento

```python
PROCESSING_CONFIG = {
    "aggregation": {
        "intervals": ["1m", "5m", "1h"],
        "operations": ["sum", "avg", "max", "p95"]
    },
    "retention": {
        "raw": "7d",
        "aggregated": "30d"
    },
    "rules": {
        "recording": {
            "request_rate": "rate(requests_total[5m])",
            "error_rate": "rate(errors_total[5m])",
            "latency_p95": "histogram_quantile(0.95, rate(latency_seconds_bucket[5m]))"
        }
    }
}
```

## Dashboards

### LLM Performance

```python
LLM_DASHBOARD = {
    "title": "LLM Performance",
    "refresh": "10s",
    "panels": [
        {
            "title": "Requisições por Minuto",
            "type": "graph",
            "query": 'rate(llm_requests_total[1m])'
        },
        {
            "title": "Latência (p95)",
            "type": "gauge",
            "query": 'histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m]))'
        },
        {
            "title": "Tokens por Segundo",
            "type": "graph",
            "query": 'rate(llm_tokens_total[1m])'
        }
    ]
}
```

### Crawler Status

```python
CRAWLER_DASHBOARD = {
    "title": "Crawler Status",
    "refresh": "30s",
    "panels": [
        {
            "title": "Páginas por Minuto",
            "type": "graph",
            "query": 'rate(crawler_pages_total[1m])'
        },
        {
            "title": "Tempo Médio por Página",
            "type": "gauge",
            "query": 'rate(crawler_duration_seconds_sum[5m]) / rate(crawler_duration_seconds_count[5m])'
        },
        {
            "title": "Tamanho da Fila",
            "type": "gauge",
            "query": 'crawler_queue_size'
        }
    ]
}
```

## Alertas

### Configuração

```python
ALERT_CONFIG = {
    "channels": {
        "slack": {
            "webhook": "https://hooks.slack.com/...",
            "channel": "#alerts"
        },
        "email": {
            "from": "alerts@synapse.ai",
            "to": ["team@synapse.ai"]
        }
    },
    "severity_levels": {
        "critical": {
            "channels": ["slack", "email"],
            "repeat": "5m"
        },
        "warning": {
            "channels": ["slack"],
            "repeat": "15m"
        }
    }
}
```

### Regras

```python
ALERT_RULES = {
    "high_error_rate": {
        "condition": "rate(errors_total[5m]) > 0.1",
        "severity": "critical",
        "annotations": {
            "summary": "Alta taxa de erros",
            "description": "Taxa de erros > 10% nos últimos 5 minutos"
        }
    },
    "high_latency": {
        "condition": "histogram_quantile(0.95, rate(latency_seconds_bucket[5m])) > 2",
        "severity": "warning",
        "annotations": {
            "summary": "Latência alta",
            "description": "Latência p95 > 2s nos últimos 5 minutos"
        }
    },
    "queue_full": {
        "condition": "crawler_queue_size > 1000",
        "severity": "warning",
        "annotations": {
            "summary": "Fila cheia",
            "description": "Fila do crawler com mais de 1000 itens"
        }
    }
}
```

## Próximos Passos

1. Implementar métricas de negócio
2. Adicionar mais dashboards
3. Refinar alertas
4. Otimizar retenção
5. Melhorar documentação 