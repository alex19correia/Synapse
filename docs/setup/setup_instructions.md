# Instruções de Setup

## Pré-requisitos
- Node.js 18+
- npm/yarn
- Redis (para desenvolvimento local)
- Conta no Clerk
- Conta no Upstash

## 1. Configuração do Ambiente

### 1.1 Clone o Repositório
```bash
git clone <repo-url>
cd agenteai
```

### 1.2 Instale as Dependências
```bash
npm install
```

### 1.3 Configure as Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Configure as seguintes variáveis:

#### Clerk (Autenticação)
1. Crie uma conta em [clerk.dev](https://clerk.dev)
2. Crie uma nova aplicação
3. Copie as chaves:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```

#### Upstash Redis (Rate Limiting)
1. Crie uma conta em [upstash.com](https://upstash.com)
2. Crie um novo banco Redis
3. Copie as credenciais:
   ```env
   UPSTASH_REDIS_REST_URL=https://...
   UPSTASH_REDIS_REST_TOKEN=AWhN...
   ```

#### LangFuse (Monitoramento)
1. Crie uma conta em [langfuse.com](https://langfuse.com)
2. Configure um novo projeto
3. Adicione as chaves:
   ```env
   LANGFUSE_PUBLIC_KEY=pk_...
   LANGFUSE_SECRET_KEY=sk_...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

## 2. Desenvolvimento

### 2.1 Inicie o Servidor
```bash
npm run dev
```

### 2.2 Execute os Testes
```bash
# Todos os testes
npm test

# Apenas testes do middleware
npm run test:middleware

# Testes manuais
npm run test:manual
```

### 2.3 Estrutura do Projeto
```
src/
├── app/          # Componentes Next.js
├── config/       # Configurações
├── lib/          # Bibliotecas e utilitários
├── middleware/   # Middlewares da aplicação
├── scripts/      # Scripts de teste/utilidade
└── tests/        # Testes automatizados

docs/
├── architecture/ # Documentação da arquitetura
├── setup/        # Instruções de setup
└── testing/      # Documentação de testes
```

## 3. Segurança

### 3.1 Autenticação
- Todas as rotas protegidas requerem autenticação via Clerk
- MFA é obrigatório para endpoints sensíveis
- Tokens JWT são validados no middleware

### 3.2 Rate Limiting
- 100 requisições por minuto por IP
- Headers de rate limit incluídos nas respostas
- Configurável via variáveis de ambiente

## 4. Monitoramento

### 4.1 LangFuse
- Métricas de uso da API
- Logs de erros
- Alertas configuráveis

### 4.2 Logs
- Logs de desenvolvimento em `NODE_ENV=development`
- Logs estruturados em produção
- Rastreamento de erros com stack traces

## 5. Troubleshooting

### 5.1 Problemas Comuns
1. **Erro de Autenticação**
   - Verifique as chaves do Clerk
   - Confirme se o token está correto
   - Verifique os logs do middleware

2. **Rate Limiting**
   - Confirme as credenciais do Upstash
   - Verifique a conectividade com Redis
   - Ajuste os limites se necessário

3. **Testes Falhando**
   - Limpe o cache do Jest
   - Verifique os mocks
   - Confirme as variáveis de ambiente 