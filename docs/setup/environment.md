# Ambiente de Desenvolvimento

## Visão Geral
```python
environment = {
    "node": "18.x",
    "package_manager": "npm",
    "framework": "Next.js 14",
    "language": "TypeScript",
    "editor": "VS Code"
}
```

## Requisitos

### 1. Node.js
- Versão: 18.x LTS
- Gerenciador: nvm (recomendado)
- Instalação:
  ```bash
  nvm install 18
  nvm use 18
  ```

### 2. Dependências
```json
{
  "dependencies": {
    "next": "14.0.4",
    "@clerk/nextjs": "4.29.3",
    "@upstash/redis": "latest",
    "tailwindcss": "latest"
  },
  "devDependencies": {
    "typescript": "5.3.3",
    "@types/node": "20.10.6",
    "@types/react": "18.2.46"
  }
}
```

### 3. Variáveis de Ambiente
```env
# Autenticação
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Redis
UPSTASH_REDIS_REST_URL=https://<region>.upstash.io
UPSTASH_REDIS_REST_TOKEN=AYz....

# Configuração
PORT=3001
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3001
```

## Setup

### 1. Instalação
```bash
# Clonar repositório
git clone https://github.com/user/agenteAI.git
cd agenteAI

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
```

### 2. Desenvolvimento
```bash
# Iniciar servidor
npm run dev

# Build
npm run build

# Testes
npm run test
npm run test:e2e
```

### 3. VS Code
Extensões recomendadas:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript + JavaScript

## Estrutura de Arquivos

### 1. Código Fonte
```
src/
├── app/           # Páginas e rotas
├── components/    # Componentes React
├── lib/          # Utilitários e serviços
├── config/       # Configurações
└── types/        # Tipos TypeScript
```

### 2. Configuração
```
├── .env.example          # Template de variáveis
├── .env.local           # Variáveis locais
├── next.config.js       # Config Next.js
├── tailwind.config.js   # Config Tailwind
└── tsconfig.json        # Config TypeScript
```

## Scripts

### 1. Desenvolvimento
```bash
# Servidor de desenvolvimento
npm run dev

# Limpar cache
Remove-Item -Recurse -Force .next
npm run clean
```

### 2. Build e Deploy
```bash
# Build de produção
npm run build

# Iniciar em produção
npm run start
```

### 3. Testes
```bash
# Testes unitários
npm run test
npm run test:watch

# Testes E2E
npm run test:e2e
```

## Troubleshooting

### 1. Problemas Comuns
1. **Erro de porta em uso**
   - Verificar se porta 3001 está livre
   - Alterar porta em `.env.local`

2. **Erros de TypeScript**
   - Limpar cache: `npm run clean`
   - Verificar tipos: `npm run type-check`

3. **Problemas de cache**
   - Limpar cache Next.js
   - Reinstalar dependências

### 2. Logs
- `npm run dev`: Console do servidor
- Chrome DevTools: Erros de cliente
- `.next/error.log`: Logs de build

## Melhores Práticas

### 1. Código
- Usar TypeScript strict mode
- Seguir ESLint airbnb-base
- Documentar funções complexas
- Manter componentes pequenos

### 2. Git
- Branches: feature/, fix/, docs/
- Commits: Conventional Commits
- PR: Templates preenchidos
- Review: Obrigatório

### 3. Testes
- Unitários: Jest + React Testing Library
- E2E: Cypress
- Coverage: >80%
- CI: GitHub Actions 