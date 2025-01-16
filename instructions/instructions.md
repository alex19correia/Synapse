# Synapse Assistant - Instruções de Desenvolvimento 🤖

## 📋 Metadata
```python
project_metadata = {
    "name": "Synapse Assistant",
    "version": "1.2.3",
    "last_update": "2024-01-10",
    "status": "active_development",
    "language": "pt-PT",
    "description": "Assistente pessoal de IA para Alexandre Correia (23 anos)",
    "objective": "Criar vantagem competitiva através de IA personalizada",
    "stack": {
        "frontend": "Next.js 14",
        "backend": "FastAPI",
        "auth": "Clerk",
        "cache": "Upstash Redis",
        "monitoring": "Grafana",
        "testing": {
            "e2e": "Playwright",
            "unit": "Jest"
        },
        "ai": {
            "primary_model": "DeepSeek V3",
            "features": ["Multi-model support", "Cost optimization"]
        }
    }
}
```

## 📁 Estrutura do Projeto
```
🚀 synapse/
├── ⚙️ config/                  # Configurações do sistema
│   ├── 📁 grafana/            # Monitoramento
│   │   ├── 📋 api_performance.json
│   │   └── 📋 rag_metrics.json
│   └── 📁 prometheus/         # Métricas
│       └── ⚙️ api_alerts.yml
├── 📚 docs/                   # Documentação
│   ├── 📁 agents/            # Documentação dos agentes
│   │   ├── 📝 github_assistant.md
│   │   └── 📝 web_researcher.md
│   ├── 📁 architecture/      # Arquitetura do sistema
│   │   ├── 📝 api-system.md
│   │   ├── 📝 llm-system.md
│   │   ├── 📝 memory-system.md
│   │   ├── 📝 analytics-system.md  # Sistema de analytics
│   │   └── 📝 security-system.md   # Sistema de segurança
│   └── 📁 llm/              # Documentação LLM
│       ├── 📝 architecture.md
│       └── 📝 technical_stack.md
├── 🔧 src/                   # Código fonte
│   ├── 📁 agents/           # Agentes implementados
│   │   ├── 📁 tech_stack_expert/
│   │   │   ├── 🐍 agent.py
│   │   │   └── 🐍 prompts.py
│   │   └── 📁 web_researcher/
│   │       └── 🐍 agent.py
│   ├── 📊 analytics/        # Sistema de Analytics
│   │   ├── 🐍 metrics.py    # Métricas do sistema
│   │   └── 🐍 reports.py    # Relatórios
│   ├── 🌐 api/              # API FastAPI
│   │   ├── 🐍 main.py      # Endpoints principais
│   │   ├── 🐍 chat.py      # Endpoints de chat
│   │   └── 🐍 middleware.py # Middlewares (auth, metrics)
│   ├── 📁 app/             # Frontend Next.js
│   │   ├── 📁 chat/        # Interface de chat
│   │   │   └── ⚛️ page.tsx
│   │   ├── 📁 components/  # Componentes React
│   │   │   ├── ⚛️ ChatWindow.tsx
│   │   │   └── ⚛️ MessageList.tsx
│   │   └── 🔒 auth/        # Autenticação Clerk
│   │       └── ⚛️ auth-provider.tsx
│   ├── ⚛️ core/            # Lógica core
│   │   ├── 🐍 llm.py      # Integração com LLMs
│   │   ├── 🐍 memory.py   # Sistema de memória
│   │   ├── 🐍 rag.py      # Sistema RAG
│   │   └── 🐍 orchestrator.py # Orquestrador de agentes
│   ├── 💾 cache/           # Sistema de Cache
│   │   ├── 🐍 redis_cache.py
│   │   └── 🐍 memory_cache.py
│   └── 🔌 services/        # Serviços
│       ├── 🐍 chat_service.py
│       ├── 🐍 llm_service.py
│       ├── 🐍 rag_service.py
│       ├── 🐍 auth_service.py   # Serviço de autenticação
│       └── 🐍 metrics_service.py # Serviço de métricas
├── 🧪 tests/               # Testes
│   ├── 📁 e2e/            # Testes end-to-end
│   │   ├── 📘 chat.e2e.ts
│   │   └── 📘 auth.e2e.ts # Testes de autenticação
│   └── 📁 unit/           # Testes unitários
│       ├── 🐍 test_rag_service.py
│       └── 🐍 test_analytics.py
├── ⚙️ docker-compose.monitoring.yml
├── 📋 package.json
├── 📝 README.md
└── 📄 requirements.txt
```

## 🚀 Missão Principal
1. **Conhecimento Personalizado** 📚
   - Compreender profundamente o Alexandre
   - Adaptar-se ao seu estilo de comunicação
   - Manter contexto histórico das interações

2. **Vantagem Competitiva** 🚀
   - Antecipar tendências tecnológicas
   - Identificar oportunidades de aprendizagem
   - Sugerir melhorias e otimizações

3. **Simplicidade e Evolução** 💡
   - Interface intuitiva e fácil de usar
   - Evolução orgânica baseada no uso
   - Auto-sugestão de melhorias

## 🚀 Status de Implementação

### ✅ Completo
1. Setup inicial do projeto
   - Next.js 14 configurado
   - TypeScript habilitado
   - TailwindCSS instalado
2. Configuração base
   - ESLint e Prettier
   - Estrutura de pastas
   - Configurações do TypeScript
3. Estrutura de documentação
   - Arquitetura definida
   - Padrões estabelecidos
   - Documentação inicial
4. API Base & CLI
   - FastAPI configurado
   - CORS habilitado
   - Health check implementado
   - CLI funcional com comandos:
     - `synapse chat`
     - `synapse verify`
     - `synapse config`
5. Integração LLM
   - DeepSeek V3 API integrado
   - Streaming e non-streaming suportados
   - Gestão de erros implementada
   - Configuração via variáveis de ambiente
6. Docker Infrastructure
   - Docker Compose completo
   - Redis (porta 6380)
   - Qdrant configurado
   - Network `synapse_network`
   - Volumes persistentes
   - Monitoramento (Prometheus/Grafana)

### 🔄 Em Progresso
1. Web Application (Reconstrução)
   - [ ] Rebuild com Lovable
   - [ ] Autenticação Clerk
   - [ ] Interface de chat
   - [ ] Integração API

2. Sistema de Chat Avançado
   - [ ] Persistência de histórico
   - [ ] Capacidades RAG com Qdrant
   - [ ] Gestão de rate limits
   - [ ] Function calling
   - [ ] Gestão de sessões

3. Monitoramento & Métricas
   - [ ] Métricas de uso da API
   - [ ] Dashboards personalizados
   - [ ] Alertas

### ⏳ Próximos Passos
1. Implementar persistência de conversas
2. Adicionar sistema RAG
3. Melhorar gestão de erros e quotas
4. Implementar features avançadas de chat

## 🔍 Sessão Atual (10/01/2024)
**Foco**: Implementação de Autenticação e Testes
**Status**: Setup inicial completo, prosseguindo com autenticação
**Progresso**:
1. ✅ Health check implementado e testado
2. ✅ Integração Docker funcionando
3. ⏳ Implementação da autenticação

**Arquivos Relevantes**:
- `src/api/main.py` - API FastAPI
- `tests/e2e/smoke.e2e.ts` - Testes de smoke
- `playwright.config.ts` - Configuração de testes
- `docker-compose.yml` - Configuração dos containers

## 🛠️ Comandos Úteis
```bash
# Desenvolvimento
npm run dev                    # Iniciar servidor de desenvolvimento
docker-compose up api          # Iniciar API FastAPI
docker-compose up              # Iniciar todos os serviços

# Monitoramento
docker-compose -f docker-compose.monitoring.yml up    # Iniciar stack de monitoramento
docker-compose -f docker-compose.monitoring.yml down  # Parar stack de monitoramento
curl localhost:9090/metrics                          # Ver métricas Prometheus
curl localhost:3000/api/metrics/health               # Verificar status do coletor

# Testes
npm run test:e2e              # Todos os testes E2E
npm run test:e2e:smoke        # Testes de smoke
npm run test:e2e:ui           # Interface gráfica do Playwright
npm run test:e2e:debug        # Modo debug

# Cache e Limpeza
docker-compose down           # Parar todos os containers
npm run clean                 # Limpar builds e cache

# Linting e Formatação
npm run lint                  # Verificar ESLint
npm run format               # Formatar com Prettier
```

## 📚 Referências
- [Documentação Principal](docs/README.md)
- [Sistema de Autenticação](docs/architecture/auth-system.md)
- [Configurações de Segurança](docs/architecture/security-system.md)
- [Sistema de Monitoramento](docs/architecture/monitoring-system.md)

## 🔐 Variáveis de Ambiente
```env
# Autenticação
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Redis
UPSTASH_REDIS_REST_URL=https://<region>.upstash.io
UPSTASH_REDIS_REST_TOKEN=AYz....

# Monitoramento
METRICS_API=http://localhost:8000
PROMETHEUS_URL=http://localhost:9090
POSTHOG_API_KEY=phc_...
METRICS_BATCH_SIZE=50
METRICS_FLUSH_INTERVAL=60000

# API
PORT=8000
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3001
```

## 📝 Notas para o Agente
1. Manter o foco na simplicidade e utilidade real
2. Priorizar funcionalidades que trazem valor imediato
3. Permitir que o assistente sugira suas próprias melhorias
4. Adaptar-se continuamente às necessidades do Alexandre
5. Manter esta estrutura atualizada a cada sessão

### Convenções de Commits
```
feat: nova funcionalidade
fix: correção de bug
docs: atualização de documentação
style: formatação, semicolons, etc
refactor: refatoração de código
test: adição/modificação de testes
chore: atualização de tarefas
```

### Padrões de Código
1. TypeScript strict mode
2. ESLint airbnb-base
3. Prettier para formatação
4. Conventional Commits
5. Testes para novas funcionalidades

## 🎨 Integração Lovable

### Visão Geral
```python
lovable_integration = {
    "propósito": "Desenvolvimento rápido de UI com proteção de código",
    "status": "Em implementação",
    "última_atualização": "2024-01-11",
    "responsável": "Alexandre Correia"
}
```

### Estrutura de Diretórios Protegidos
```
src/
├── components/
│   ├── lovable/     # Componentes gerados pelo Lovable
│   └── custom/      # Componentes customizados
├── app/
│   ├── (lovable)/   # Páginas geradas pelo Lovable
│   └── [outras]/    # Outras páginas da aplicação
└── styles/
    └── lovable/     # Estilos gerados pelo Lovable
```

### Sistema de Proteção
```typescript
// Marcadores de Proteção
const LOVABLE_MARKERS = {
  start: '/** @generated-by-lovable - DO NOT EDIT */',
  end: '/** @end-lovable */'
}
```

### Workflow de Desenvolvimento
1. **Criar no Lovable**
   - Desenvolver componentes/páginas
   - Testar funcionalidade
   - Exportar código

2. **Proteger e Importar**
   ```bash
   # Executar script de proteção
   npm run protect-lovable
   ```

3. **Desenvolvimento Contínuo**
   - Código protegido em diretórios específicos
   - Desenvolvimento normal continua em outras áreas
   - Atualizações via Lovable quando necessário

### Comandos de Integração
```bash
# Proteção de Código Lovable
npm run protect-lovable        # Proteger código exportado
npm run verify-lovable        # Verificar integridade

# Desenvolvimento
npm run dev:lovable           # Ambiente de desenvolvimento Lovable
npm run build:lovable        # Build de componentes Lovable
```

### Melhores Práticas
1. **Organização**
   - Manter componentes Lovable isolados
   - Usar convenção de nomes clara
   - Documentar integrações

2. **Versionamento**
   - Commits separados para código Lovable
   - Tags para versões importantes
   - Branches específicos se necessário

3. **Manutenção**
   - Backups regulares
   - Verificações de integridade
   - Atualizações documentadas

### Notas Importantes
1. Nunca editar código dentro dos marcadores de proteção
2. Sempre usar o script de proteção ao importar
3. Manter documentação atualizada
4. Fazer backup antes de grandes atualizações

## 📊 Sistema de Métricas

### Arquitetura
```python
metrics_system = {
    "client": {
        "type": "TypeScript BatchCollector",
        "features": ["batch_processing", "error_handling", "auto_flush"],
        "config": {
            "batch_size": 50,
            "flush_interval": 60000  # 60 segundos
        }
    },
    "api": {
        "gateway": "Next.js API Routes",
        "backend": "FastAPI Endpoints",
        "validation": "Pydantic Schemas"
    },
    "storage": {
        "primary": "Prometheus",
        "cache": "Redis",
        "analytics": "PostHog"
    }
}
```

### Tipos de Métricas
1. **LLM Metrics**
   - Requests, duração, tokens
   - Taxa de sucesso
   - Modelo utilizado

2. **Cache Metrics**
   - Hit/miss ratio
   - Operações por tipo
   - Performance

3. **User Metrics**
   - Atividade por usuário
   - Duração de sessão
   - Padrões de uso

4. **System Metrics**
   - Logs por nível
   - Erros por componente
   - Uso de memória
   - Performance de API

### Rate Limiting
```python
rate_limits = {
    "error": 1000,    # Métricas de erro (por minuto)
    "batch": 100,     # Batches por minuto
    "default": 500    # Outras métricas individuais
}
```

### Batch Processing
- Coleta em lote para reduzir chamadas API
- Flush automático por tamanho ou tempo
- Retry em caso de falha
- Headers para validação de batch

## 🔄 Em Progresso (13/01/2024)
1. **Sistema de Métricas**
   - ✅ Batch processing implementado
   - ✅ Rate limiting configurado
   - ✅ Validação com Pydantic
   - ⏳ Dashboards Prometheus

2. **Chat Inteligente**
   - ⏳ Sistema de memória e contexto
   - ⏳ Perfil personalizado
   - ⏳ Integração com LLMs

3. **Sistema de Conhecimento**
   - ⏳ Armazenamento de informações
   - ⏳ Gestão de documentos
   - ⏳ Manutenção de contexto
