# Sistema de Monitoramento

## Visão Geral
O sistema de monitoramento é responsável por coletar, visualizar e alertar sobre o estado dos diferentes componentes da aplicação, incluindo LLM, crawlers e infraestrutura.

## Arquitetura

### Componentes

```python
MONITORING_COMPONENTS = {
    "Prometheus": {
        "description": "Coleta e armazenamento de métricas",
        "endpoints": [
            "/metrics",
            "/api/v1/query",
            "/api/v1/query_range"
        ],
        "storage": {
            "retention": "15d",
            "compaction": True
        }
    },
    "Grafana": {
        "description": "Visualização e alertas",
        "features": [
            "Dashboards customizados",
            "Alertas configuráveis",
            "Integração com Slack/Email"
        ]
    }
}
```

### Métricas Coletadas

```python
METRICS = {
    "System": {
        "cpu_usage": {
            "type": "gauge",
            "labels": ["component"]
        },
        "memory_usage": {
            "type": "gauge",
            "labels": ["component"]
        },
        "disk_usage": {
            "type": "gauge",
            "labels": ["mount"]
        }
    },
    "Application": {
        "llm": {
            "requests": "counter",
            "latency": "histogram",
            "errors": "counter"
        },
        "crawler": {
            "pages": "counter",
            "duration": "histogram",
            "errors": "counter"
        },
        "cache": {
            "hits": "counter",
            "misses": "counter",
            "size": "gauge"
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
            "title": "Cache Hit Rate",
            "type": "graph",
            "query": 'rate(llm_cache_hits_total[5m]) / rate(llm_cache_operations_total[5m])'
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
            "title": "Erros por Tipo",
            "type": "pie",
            "query": 'crawler_errors_total'
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
    "llm_errors": {
        "condition": "rate(llm_requests_total{status='error'}[5m]) > 0.1",
        "severity": "critical",
        "annotations": {
            "summary": "Alta taxa de erros no LLM",
            "description": "Taxa de erros > 10% nos últimos 5 minutos"
        }
    },
    "crawler_slow": {
        "condition": "rate(crawler_duration_seconds_sum[5m]) / rate(crawler_duration_seconds_count[5m]) > 30",
        "severity": "warning",
        "annotations": {
            "summary": "Crawler lento",
            "description": "Tempo médio por página > 30 segundos"
        }
    }
}
```

## Logs

### Configuração

```python
LOG_CONFIG = {
    "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    "format": "{timestamp} {level} {component}: {message}",
    "outputs": [
        {
            "type": "file",
            "path": "/var/log/synapse.log",
            "rotation": "1d"
        },
        {
            "type": "stdout",
            "format": "colored"
        }
    ]
}
```

## Próximos Passos

1. Implementar métricas de negócio
2. Adicionar tracing distribuído
3. Melhorar visualizações
4. Configurar retenção de logs
5. Adicionar mais alertas 