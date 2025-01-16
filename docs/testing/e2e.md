# Testes E2E

## Visão Geral
```python
e2e_testing = {
    "framework": "Cypress",
    "status": "planned",
    "coverage": {
        "auth": ["login", "signup", "logout"],
        "api": ["rate limiting", "errors"],
        "ui": ["navigation", "forms"]
    }
}
```

## Setup

### 1. Instalação
```bash
# Instalar Cypress
npm install cypress --save-dev

# Configurar TypeScript
npm install @cypress/typescript-preprocessor --save-dev
```

### 2. Configuração
```typescript
// cypress.config.ts
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3001',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    video: false,
    screenshotOnRunFailure: true,
    viewportWidth: 1280,
    viewportHeight: 720
  }
})
```

## Estrutura de Testes

### 1. Autenticação
```typescript
// cypress/e2e/auth/login.cy.ts
describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('should show login form', () => {
    cy.get('[data-testid="login-form"]').should('exist')
  })

  it('should handle invalid credentials', () => {
    cy.get('[data-testid="email-input"]').type('invalid@email.com')
    cy.get('[data-testid="password-input"]').type('wrongpassword')
    cy.get('[data-testid="login-button"]').click()
    cy.get('[data-testid="error-message"]').should('be.visible')
  })

  it('should login successfully', () => {
    cy.get('[data-testid="email-input"]').type(Cypress.env('TEST_USER_EMAIL'))
    cy.get('[data-testid="password-input"]').type(Cypress.env('TEST_USER_PASSWORD'))
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/dashboard')
  })
})
```

### 2. API
```typescript
// cypress/e2e/api/rate-limiting.cy.ts
describe('Rate Limiting', () => {
  it('should handle rate limiting', () => {
    // Make multiple requests
    for (let i = 0; i < 110; i++) {
      cy.request({
        url: '/api/test',
        failOnStatusCode: false
      }).then((response) => {
        if (i >= 100) {
          expect(response.status).to.eq(429)
        }
      })
    }
  })
})
```

### 3. UI/UX
```typescript
// cypress/e2e/ui/navigation.cy.ts
describe('Navigation', () => {
  beforeEach(() => {
    cy.login() // Custom command
  })

  it('should navigate through main sections', () => {
    cy.get('[data-testid="nav-dashboard"]').click()
    cy.url().should('include', '/dashboard')
    
    cy.get('[data-testid="nav-profile"]').click()
    cy.url().should('include', '/profile')
  })
})
```

## Comandos Personalizados

### 1. Autenticação
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('login', (email = Cypress.env('TEST_USER_EMAIL'), password = Cypress.env('TEST_USER_PASSWORD')) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type(email)
    cy.get('[data-testid="password-input"]').type(password)
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/dashboard')
  })
})
```

### 2. Utilitários
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('clearCache', () => {
  cy.clearLocalStorage()
  cy.clearCookies()
})

Cypress.Commands.add('mockApi', (route, fixture) => {
  cy.intercept('GET', route, { fixture }).as('apiCall')
})
```

## Scripts

### 1. Execução
```bash
# Abrir Cypress
npm run cypress:open

# Rodar headless
npm run cypress:run

# Rodar específico
npm run cypress:run --spec "cypress/e2e/auth/**/*.cy.ts"
```

### 2. CI/CD
```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  cypress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cypress-io/github-action@v5
        with:
          build: npm run build
          start: npm start
          wait-on: 'http://localhost:3001'
```

## Melhores Práticas

### 1. Organização
- Agrupar por funcionalidade
- Usar data-testid
- Manter testes independentes
- Limpar estado entre testes

### 2. Performance
- Usar cy.session para login
- Evitar sleeps/waits
- Minimizar requisições reais
- Cache de autenticação

### 3. Manutenção
- Documentar comandos custom
- Usar TypeScript
- Manter fixtures atualizadas
- Revisar falhas frequentes 