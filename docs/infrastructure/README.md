# Sistema de Infraestrutura 🏗️

## Visão Geral

O sistema de Infraestrutura do Synapse Assistant gerencia todos os componentes de infraestrutura necessários para o funcionamento do sistema, incluindo servidores, bancos de dados, cache, monitoramento e deployment.

## Componentes

### 1. Servidores

#### API Server
```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 60
  keepalive: 5
```

#### Worker Server
```yaml
worker:
  processes: 2
  threads: 4
  queue_size: 100
  timeout: 300
```

### 2. Banco de Dados

#### PostgreSQL
```yaml
database:
  host: localhost
  port: 5432
  name: synapse
  user: synapse_user
  max_connections: 20
  pool_size: 5
```

#### Redis Cache
```yaml
redis:
  host: localhost
  port: 6379
  db: 0
  max_connections: 10
  timeout: 5
```

### 3. Vector Store

#### Qdrant
```yaml
qdrant:
  host: localhost
  port: 6333
  collection: documents
  vector_size: 768
  distance: Cosine
```

## Deployment

### 1. Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/synapse
    depends_on:
      - db
      - redis
      - qdrant
```

### 2. Kubernetes

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synapse-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synapse-api
  template:
    metadata:
      labels:
        app: synapse-api
    spec:
      containers:
      - name: api
        image: synapse-api:latest
        ports:
        - containerPort: 8000
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: synapse-api
spec:
  selector:
    app: synapse-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Monitoramento

### 1. Prometheus

#### Config
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

#### Dashboards
- System metrics
- Application metrics
- Database metrics
- Cache metrics

## Logging

### 1. ELK Stack

#### Logstash Config
```yaml
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "synapse-%{+YYYY.MM.dd}"
  }
}
```

### 2. Structured Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("event",
            service="api",
            endpoint="/generate",
            duration=0.5)
```

## Backup

### 1. Database

#### Backup Script
```bash
#!/bin/bash
pg_dump synapse > backup.sql
aws s3 cp backup.sql s3://backups/
```

#### Schedule
- Full backup: Daily
- WAL archiving: Continuous
- Retention: 30 days

### 2. Vector Store

#### Backup Config
```yaml
backup:
  schedule: "0 0 * * *"
  destination: s3://backups/vectors/
  retention: 7
  compression: true
```

## Segurança

### 1. Network

#### Firewall Rules
```yaml
firewall:
  inbound:
    - port: 80
      source: 0.0.0.0/0
    - port: 443
      source: 0.0.0.0/0
    - port: 22
      source: 10.0.0.0/8
```

### 2. Encryption

#### TLS Config
```yaml
tls:
  cert_file: /etc/ssl/certs/synapse.crt
  key_file: /etc/ssl/private/synapse.key
  min_version: TLSv1.2
```

## Scaling

### 1. Horizontal

#### Autoscaling
```yaml
autoscaling:
  min_replicas: 2
  max_replicas: 10
  target_cpu_utilization: 70
  cooldown_period: 300
```

### 2. Vertical

#### Resource Limits
```yaml
resources:
  limits:
    cpu: 2
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

## Disaster Recovery

### 1. Failover

#### Database Failover
```yaml
failover:
  primary: db-primary
  standby: db-standby
  automatic: true
  timeout: 30
```

### 2. Recovery

#### Recovery Plan
1. Assess impact
2. Restore from backup
3. Verify data integrity
4. Switch traffic
5. Validate system

## Manutenção

### 1. Updates

#### Update Strategy
```yaml
updates:
  schedule: "0 2 * * 0"  # Sunday 2AM
  max_unavailable: 1
  timeout: 600
  rollback: true
```

### 2. Cleanup

#### Cleanup Jobs
```yaml
cleanup:
  logs:
    retention: 30d
    compress: true
  temp:
    retention: 7d
  cache:
    retention: 1d
```

## Monitoramento

### 1. Health Checks

#### Endpoints
```yaml
health:
  - name: api
    url: /health
    interval: 30s
    timeout: 5s
  - name: db
    url: /health/db
    interval: 1m
    timeout: 10s
```

### 2. Alerting

#### Alert Rules
```yaml
alerts:
  - name: high_cpu
    condition: cpu > 80%
    duration: 5m
    severity: warning
  - name: service_down
    condition: up == 0
    duration: 1m
    severity: critical
```

## Referências

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/) 