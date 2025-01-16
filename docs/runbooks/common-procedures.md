# Procedimentos Operacionais Comuns 🛠️

## Visão Geral
Este runbook contém os procedimentos operacionais mais comuns para manutenção e operação do sistema.

## Procedimentos

### 1. Reinício de Serviços
```bash
# Reinício do servidor de aplicação
pm2 restart app

# Reinício do Redis
sudo systemctl restart redis

# Reinício do PostgreSQL
sudo systemctl restart postgresql
```

### 2. Verificação de Logs
```bash
# Logs da aplicação
pm2 logs app

# Logs do sistema
journalctl -u app -f

# Logs do Redis
tail -f /var/log/redis/redis-server.log

# Logs do PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log
```

### 3. Backup Manual
```bash
# Backup do banco de dados
pg_dump -U postgres -d synapse > backup_$(date +%Y%m%d).sql

# Backup de arquivos
tar -czf backup_files_$(date +%Y%m%d).tar.gz /path/to/files
```

### 4. Monitoramento
```bash
# Status dos serviços
pm2 status
systemctl status redis
systemctl status postgresql

# Uso de recursos
htop
df -h
free -m
```

### 5. Limpeza de Cache
```bash
# Redis
redis-cli FLUSHALL

# Temp files
rm -rf /tmp/synapse-*
```

## Troubleshooting Comum

### 1. Servidor Não Responde
1. Verificar logs: `pm2 logs app`
2. Verificar recursos: `htop`
3. Verificar conexões: `netstat -tulpn`
4. Reiniciar se necessário: `pm2 restart app`

### 2. Banco de Dados Lento
1. Verificar conexões ativas
2. Identificar queries lentas
3. Analisar índices
4. Limpar cache se necessário

### 3. Problemas de Memória
1. Verificar uso: `free -m`
2. Identificar processos: `ps aux --sort=-%mem`
3. Limpar cache se necessário
4. Reiniciar serviços problemáticos

## Manutenção Preventiva

### 1. Checklist Diário
- [ ] Verificar logs de erros
- [ ] Monitorar uso de recursos
- [ ] Verificar backups
- [ ] Validar métricas principais

### 2. Checklist Semanal
- [ ] Análise de tendências
- [ ] Limpeza de logs antigos
- [ ] Verificação de segurança
- [ ] Atualização de documentação

### 3. Checklist Mensal
- [ ] Revisão de performance
- [ ] Atualização de dependências
- [ ] Teste de recuperação
- [ ] Revisão de acessos

## Contatos de Emergência

### Time de Desenvolvimento
- Dev Lead: @dev-lead
- Backend: @backend-team
- Frontend: @frontend-team

### Time de Operações
- Ops Lead: @ops-lead
- DBA: @dba-team
- DevOps: @devops-team

## Referências
- [Sistema de Monitoramento](../architecture/monitoring-system.md)
- [Sistema de Backup](../architecture/backup-system.md)
- [Sistema de Deployment](../architecture/deployment-system.md) 