# Sistema de Analytics & Metrics 📊

## Visão Geral

O sistema de Analytics & Metrics do Synapse Assistant é responsável por coletar, processar e visualizar métricas de todos os componentes do sistema, permitindo monitoramento em tempo real e análise histórica.

## Componentes

### 1. Métricas LLM
```python
from src.analytics.metrics.llm_metrics import LLMMetrics

metrics = LLMMetrics()
await metrics.track_request(duration=0.5, tokens=100)
```

#### Métricas Coletadas
- Request count
- Token usage
- Latência
- Cache hits/misses
- Error rates
- Active requests

### 2. Métricas API
```python
from src.analytics.metrics.api_metrics import APIMetrics

metrics = APIMetrics()
await metrics.track_request(endpoint="/generate", status=200)
```

#### Métricas Coletadas
- Request count por endpoint
- Status codes
- Latência
- Request/response size
- Rate limits
- Concurrent requests

### 3. Métricas Crawler
```python
from src.analytics.metrics.crawler_metrics import CrawlerMetrics

metrics = CrawlerMetrics()
await metrics.track_crawl(url="example.com", duration=1.5)
```

#### Métricas Coletadas
- Crawl count
- Success/error rates
- Processing time
- Content size
- Rate limits
- Concurrent crawls

## Infraestrutura

### 1. Prometheus
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'synapse'
    static_configs:
      - targets: ['localhost:8000']
```

### 2. Grafana
- Dashboards customizados
- Alertas configuráveis
- Visualizações em tempo real
- Análise histórica

## Dashboards

### 1. LLM Performance
- Request volume
- Latência (p50, p95, p99)
- Cache hit ratio
- Token usage
- Error rates

### 2. API Health
- Request volume por endpoint
- Status codes distribution
- Latência por endpoint
- Rate limit usage
- Error patterns

### 3. Crawler Status
- Active crawls
- Success/error rates
- Processing time
- Content metrics
- Rate limit status

## Alertas

### 1. Latência
```yaml
alert: HighLatency
expr: llm_request_duration_seconds > 2
for: 5m
labels:
  severity: warning
annotations:
  description: "High latency detected"
```

### 2. Erros
```yaml
alert: HighErrorRate
expr: rate(llm_errors_total[5m]) > 0.1
for: 5m
labels:
  severity: critical
annotations:
  description: "High error rate detected"
```

### 3. Cache
```yaml
alert: LowCacheHitRatio
expr: rate(llm_cache_hits[5m]) / rate(llm_requests_total[5m]) < 0.5
for: 15m
labels:
  severity: warning
annotations:
  description: "Low cache hit ratio"
```

## Exportação de Dados

### 1. Prometheus API
```python
from prometheus_client import REGISTRY

def export_metrics():
    return generate_latest(REGISTRY)
```

### 2. Grafana Export
- CSV export
- JSON export
- PDF reports
- API access

## Retenção de Dados

### 1. Prometheus
- Raw data: 15 dias
- 5m aggregates: 30 dias
- 1h aggregates: 90 dias
- Daily aggregates: 1 ano

### 2. Logs
- Error logs: 30 dias
- Access logs: 15 dias
- Audit logs: 90 dias

## Monitoramento

### 1. Health Checks
```python
async def check_metrics_health():
    metrics_up = await check_prometheus()
    grafana_up = await check_grafana()
    return metrics_up and grafana_up
```

### 2. Performance Checks
- Scrape duration
- Storage usage
- Query performance
- Dashboard load time

## Segurança

### 1. Acesso
- Authentication required
- Role-based access
- API tokens
- Audit logging

### 2. Dados Sensíveis
- Data masking
- Encryption at rest
- Secure transport
- Access controls

## Manutenção

### 1. Backup
- Daily snapshots
- Retention policies
- Recovery procedures
- Validation checks

### 2. Cleanup
- Old data purge
- Index optimization
- Storage compaction
- Cache cleanup

## Troubleshooting

### 1. Missing Data
- Check scrape configs
- Verify endpoints
- Check storage
- Validate retention

### 2. High Load
- Optimize queries
- Adjust retention
- Scale storage
- Load balancing

### 3. Alert Storms
- Adjust thresholds
- Group alerts
- Add dampening
- Review triggers

## Referências

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Metrics Best Practices](https://prometheus.io/docs/practices/naming/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) 