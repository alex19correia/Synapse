# Guia de Troubleshooting 🔍

## Visão Geral
Este guia contém procedimentos detalhados para diagnóstico e resolução dos problemas mais comuns encontrados no sistema.

## Problemas Comuns

### 1. Problemas de Performance

#### Latência Alta na API
```python
diagnóstico = {
    "sintomas": [
        "Tempo de resposta > 500ms",
        "Timeouts frequentes",
        "Erros 503"
    ],
    "verificações": [
        "Monitorar uso de CPU/Memória",
        "Verificar logs de erro",
        "Analisar métricas de DB"
    ],
    "causas_comuns": [
        "Sobrecarga de recursos",
        "Queries lentas",
        "Cache ineficiente"
    ],
    "soluções": [
        "Otimizar queries críticas",
        "Ajustar configuração de cache",
        "Escalar recursos se necessário"
    ]
}
```

#### Memória Alta
```python
diagnóstico = {
    "sintomas": [
        "Uso de memória > 80%",
        "Swapping frequente",
        "OOM Killer ativo"
    ],
    "verificações": [
        "top -o %MEM",
        "free -m",
        "dmesg | grep -i kill"
    ],
    "soluções": [
        "Identificar memory leaks",
        "Ajustar limites de memória",
        "Otimizar cache"
    ]
}
```

### 2. Problemas de Conectividade

#### Falhas de Rede
```python
diagnóstico = {
    "sintomas": [
        "Timeouts de conexão",
        "Latência alta",
        "Pacotes perdidos"
    ],
    "verificações": [
        "ping para endpoints",
        "traceroute",
        "verificar DNS"
    ],
    "ferramentas": [
        "netstat -tulpn",
        "tcpdump",
        "wireshark"
    ],
    "soluções": [
        "Verificar firewall",
        "Ajustar timeouts",
        "Validar DNS"
    ]
}
```

#### Problemas de SSL/TLS
```python
diagnóstico = {
    "sintomas": [
        "Erros de certificado",
        "Handshake falhou",
        "Conexão recusada"
    ],
    "verificações": [
        "Validade do certificado",
        "Configuração SSL",
        "Versões suportadas"
    ],
    "comandos": [
        "openssl s_client -connect host:443",
        "curl -v https://host",
        "ssllabs-scan host"
    ]
}
```

### 3. Problemas de Banco de Dados

#### Queries Lentas
```python
diagnóstico = {
    "sintomas": [
        "Tempo de resposta alto",
        "CPU elevada no DB",
        "Bloqueios frequentes"
    ],
    "análise": [
        "Verificar slow query log",
        "Analisar planos de execução",
        "Monitorar locks"
    ],
    "soluções": [
        "Otimizar índices",
        "Ajustar queries",
        "Configurar statement timeout"
    ]
}
```

#### Conexões Esgotadas
```python
diagnóstico = {
    "sintomas": [
        "Erros de conexão",
        "Timeouts frequentes",
        "Pool esgotado"
    ],
    "verificações": [
        "show processlist",
        "pg_stat_activity",
        "netstat | grep postgres"
    ],
    "soluções": [
        "Ajustar pool size",
        "Limpar conexões zumbis",
        "Configurar timeout"
    ]
}
```

### 4. Problemas de Cache

#### Cache Miss Alto
```python
diagnóstico = {
    "sintomas": [
        "Hit rate < 80%",
        "Latência aumentada",
        "Load alto no DB"
    ],
    "verificações": [
        "Monitorar hit rate",
        "Analisar padrões de acesso",
        "Verificar invalidações"
    ],
    "soluções": [
        "Ajustar TTL",
        "Revisar estratégia",
        "Pré-aquecer cache"
    ]
}
```

#### Inconsistência de Cache
```python
diagnóstico = {
    "sintomas": [
        "Dados desatualizados",
        "Comportamento inconsistente",
        "Erros de validação"
    ],
    "verificações": [
        "Logs de invalidação",
        "Padrões de atualização",
        "Configuração de TTL"
    ],
    "soluções": [
        "Implementar cache aside",
        "Usar versioning",
        "Ajustar invalidação"
    ]
}
```

## Ferramentas de Diagnóstico

### 1. Monitoramento
```python
ferramentas = {
    "métricas": {
        "prometheus": "Coleta de métricas",
        "grafana": "Visualização",
        "alertmanager": "Alertas"
    },
    "logs": {
        "elasticsearch": "Armazenamento",
        "kibana": "Visualização",
        "fluentd": "Coleta"
    },
    "tracing": {
        "jaeger": "Distributed tracing",
        "zipkin": "Trace visualization"
    }
}
```

### 2. Debugging
```python
ferramentas = {
    "profiling": {
        "py-spy": "Python profiling",
        "perf": "Linux perf events",
        "flame graphs": "Visualização"
    },
    "network": {
        "tcpdump": "Packet capture",
        "wireshark": "Análise de pacotes",
        "mtr": "Network paths"
    },
    "database": {
        "pg_stat_statements": "Query stats",
        "explain analyze": "Query plans",
        "pgbadger": "Log analysis"
    }
}
```

## Procedimentos de Escalação

### 1. Níveis de Severidade
```python
severidade = {
    "crítico": {
        "descrição": "Serviço indisponível",
        "sla": "30 minutos",
        "notificação": "Imediata",
        "equipe": "24/7"
    },
    "alto": {
        "descrição": "Funcionalidade crítica afetada",
        "sla": "2 horas",
        "notificação": "Imediata",
        "equipe": "Horário comercial"
    },
    "médio": {
        "descrição": "Funcionalidade não-crítica",
        "sla": "8 horas",
        "notificação": "Email",
        "equipe": "Horário comercial"
    }
}
```

### 2. Matriz de Escalação
```python
escalação = {
    "nível_1": {
        "equipe": "Suporte L1",
        "tempo": "15 minutos",
        "ações": ["Diagnóstico inicial", "Soluções conhecidas"]
    },
    "nível_2": {
        "equipe": "Suporte L2",
        "tempo": "30 minutos",
        "ações": ["Análise técnica", "Correções complexas"]
    },
    "nível_3": {
        "equipe": "Desenvolvimento",
        "tempo": "1 hora",
        "ações": ["Debug avançado", "Correções de código"]
    }
}
```

## Melhores Práticas

### 1. Coleta de Informações
1. Identificar sintomas específicos
2. Coletar logs relevantes
3. Capturar métricas do período
4. Documentar passos de reprodução

### 2. Análise
1. Estabelecer linha do tempo
2. Identificar padrões
3. Correlacionar eventos
4. Testar hipóteses

### 3. Resolução
1. Implementar correção
2. Validar solução
3. Monitorar resultados
4. Documentar aprendizados

## Referências
- [Sistema de Monitoramento](../architecture/monitoring-system.md)
- [Sistema de Logs](../architecture/logging-system.md)
- [Procedimentos de Backup](./disaster-recovery.md) 