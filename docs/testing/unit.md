# Testes Unitários

## Visão Geral
```python
unit_testing = {
    "framework": "Jest",
    "runner": "React Testing Library",
    "status": "planned",
    "coverage": {
        "target": "80%",
        "current": "0%",
        "areas": [
            "Components",
            "Hooks",
            "Utils",
            "API"
        ]
    }
}
```

## Setup

### 1. Instalação
```bash
# Jest e Testing Library
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# TypeScript support
npm install --save-dev @types/jest ts-jest
```

### 2. Configuração
```typescript
// jest.config.ts
import type { Config } from 'jest'

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/types/**/*'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}

export default config
```

## Estrutura de Testes

### 1. Componentes
```typescript
// src/components/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('should render correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('should handle click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when loading', () => {
    render(<Button loading>Loading...</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### 2. Hooks
```typescript
// src/hooks/useAuth/useAuth.test.ts
import { renderHook, act } from '@testing-library/react'
import { useAuth } from './useAuth'

describe('useAuth', () => {
  it('should return auth state', () => {
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAuthenticated).toBeDefined()
  })

  it('should handle login', async () => {
    const { result } = renderHook(() => useAuth())
    
    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password'
      })
    })

    expect(result.current.isAuthenticated).toBe(true)
  })
})
```

### 3. Utils
```typescript
// src/utils/format/format.test.ts
import { formatDate, formatCurrency } from './format'

describe('formatDate', () => {
  it('should format date correctly', () => {
    const date = new Date('2024-01-10')
    expect(formatDate(date)).toBe('10/01/2024')
  })
})

describe('formatCurrency', () => {
  it('should format currency correctly', () => {
    expect(formatCurrency(1234.56)).toBe('€1,234.56')
  })
})
```

### 4. API
```typescript
// src/api/auth/auth.test.ts
import { login, logout } from './auth'

describe('Auth API', () => {
  beforeEach(() => {
    fetchMock.resetMocks()
  })

  it('should handle successful login', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ token: 'fake-token' }))

    const response = await login({
      email: 'test@example.com',
      password: 'password'
    })

    expect(response.token).toBe('fake-token')
  })

  it('should handle login errors', async () => {
    fetchMock.mockRejectOnce(new Error('Invalid credentials'))

    await expect(login({
      email: 'invalid@example.com',
      password: 'wrong'
    })).rejects.toThrow('Invalid credentials')
  })
})
```

## Mocks e Fixtures

### 1. Providers
```typescript
// src/test/providers.tsx
export const TestProvider: React.FC = ({ children }) => (
  <ClerkProvider>
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  </ClerkProvider>
)

export const renderWithProviders = (ui: React.ReactElement) => {
  return render(ui, { wrapper: TestProvider })
}
```

### 2. Mocks
```typescript
// src/test/mocks/auth.ts
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User'
}

export const mockAuthState = {
  isAuthenticated: true,
  user: mockUser,
  loading: false
}
```

## Scripts

### 1. Execução
```bash
# Rodar todos os testes
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### 2. CI/CD
```yaml
# .github/workflows/unit.yml
name: Unit Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
```

## Melhores Práticas

### 1. Organização
- Um arquivo de teste por módulo
- Agrupar testes relacionados
- Manter fixtures separadas
- Usar helpers comuns

### 2. Performance
- Minimizar uso de beforeAll/beforeEach
- Limpar mocks após cada teste
- Evitar testes acoplados
- Usar mocks com moderação

### 3. Manutenção
- Documentar casos complexos
- Manter cobertura alta
- Revisar testes falhos
- Atualizar snapshots com cuidado 