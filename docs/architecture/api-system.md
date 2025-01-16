# Sistema de API

## Visão Geral
```python
api_system = {
    "framework": "tRPC",
    "status": "planned",
    "features": [
        "Type-safe APIs",
        "Rate Limiting",
        "Authentication",
        "Validation"
    ],
    "integrations": {
        "auth": "Clerk",
        "cache": "Upstash Redis",
        "monitoring": "Grafana"
    }
}
```

## Componentes Principais

### 1. Routers
```typescript
// src/app/api/trpc/routers/auth.ts
export const authRouter = createTRPCRouter({
  getSession: protectedProcedure
    .query(async ({ ctx }) => {
      return ctx.auth.session;
    }),
    
  logout: protectedProcedure
    .mutation(async ({ ctx }) => {
      await ctx.auth.signOut();
      return { success: true };
    })
});
```

### 2. Middleware
```typescript
// src/app/api/trpc/middleware.ts
export const authMiddleware = t.middleware(async ({ ctx, next }) => {
  if (!ctx.auth.userId) {
    throw new TRPCError({
      code: 'UNAUTHORIZED',
      message: 'Not authenticated'
    });
  }
  return next({
    ctx: {
      auth: ctx.auth,
      userId: ctx.auth.userId
    }
  });
});

export const rateLimitMiddleware = t.middleware(async ({ ctx, next }) => {
  const ip = ctx.req?.socket.remoteAddress || '127.0.0.1';
  const limit = await rateLimit(ip);
  
  if (!limit.success) {
    throw new TRPCError({
      code: 'TOO_MANY_REQUESTS',
      message: 'Rate limit exceeded'
    });
  }
  
  return next();
});
```

### 3. Validação
```typescript
// src/app/api/trpc/schemas/auth.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  mfaCode: z.string().optional()
});

export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  role: z.enum(['user', 'admin'])
});
```

## Endpoints

### 1. Autenticação
```typescript
// src/app/api/trpc/routers/auth.ts
export const authRouter = createTRPCRouter({
  login: publicProcedure
    .input(loginSchema)
    .mutation(async ({ input, ctx }) => {
      // Login logic
    }),
    
  register: publicProcedure
    .input(registerSchema)
    .mutation(async ({ input, ctx }) => {
      // Registration logic
    }),
    
  verifyEmail: publicProcedure
    .input(z.object({ token: z.string() }))
    .mutation(async ({ input, ctx }) => {
      // Email verification logic
    })
});
```

### 2. Usuários
```typescript
// src/app/api/trpc/routers/users.ts
export const usersRouter = createTRPCRouter({
  me: protectedProcedure
    .query(async ({ ctx }) => {
      return ctx.auth.user;
    }),
    
  updateProfile: protectedProcedure
    .input(updateProfileSchema)
    .mutation(async ({ input, ctx }) => {
      // Profile update logic
    }),
    
  updateSettings: protectedProcedure
    .input(updateSettingsSchema)
    .mutation(async ({ input, ctx }) => {
      // Settings update logic
    })
});
```

### 3. Sistema
```typescript
// src/app/api/trpc/routers/system.ts
export const systemRouter = createTRPCRouter({
  health: publicProcedure
    .query(() => ({
      status: 'healthy',
      timestamp: new Date()
    })),
    
  metrics: adminProcedure
    .query(async ({ ctx }) => {
      return await getSystemMetrics();
    })
});
```

## Segurança

### 1. Rate Limiting
```typescript
// src/lib/rate-limit.ts
export const rateLimit = async (ip: string) => {
  const key = `rate-limit:${ip}`;
  const limit = 100;
  const window = 60; // seconds
  
  const current = await redis.incr(key);
  if (current === 1) {
    await redis.expire(key, window);
  }
  
  return {
    success: current <= limit,
    remaining: Math.max(0, limit - current),
    reset: await redis.ttl(key)
  };
};
```

### 2. Autenticação
```typescript
// src/app/api/trpc/context.ts
export const createContext = async (opts: CreateNextContextOptions) => {
  const { req } = opts;
  const session = await getAuth(req);
  
  return {
    auth: session,
    redis: getRedisClient(),
    req
  };
};
```

## Monitoramento

### 1. Métricas
```typescript
// src/lib/metrics.ts
export const apiMetrics = {
  requestCount: new Counter({
    name: 'api_requests_total',
    help: 'Total number of API requests'
  }),
  
  responseTime: new Histogram({
    name: 'api_response_time_seconds',
    help: 'API response time in seconds'
  }),
  
  errorCount: new Counter({
    name: 'api_errors_total',
    help: 'Total number of API errors'
  })
};
```

### 2. Logging
```typescript
// src/lib/logger.ts
export const apiLogger = {
  request: (req: Request, meta: object) => {
    logger.info('API Request', {
      method: req.method,
      path: req.url,
      ...meta
    });
  },
  
  error: (error: Error, meta: object) => {
    logger.error('API Error', {
      message: error.message,
      stack: error.stack,
      ...meta
    });
  }
};
```

## Testes

### 1. Integration
```typescript
// tests/api/auth.test.ts
describe('Auth API', () => {
  it('should handle login', async () => {
    const caller = appRouter.createCaller({
      auth: mockAuth,
      redis: mockRedis
    });
    
    const result = await caller.auth.login({
      email: 'test@example.com',
      password: 'password'
    });
    
    expect(result.success).toBe(true);
  });
});
```

### 2. Unit
```typescript
// tests/api/middleware.test.ts
describe('API Middleware', () => {
  it('should rate limit requests', async () => {
    const ip = '127.0.0.1';
    
    // Make multiple requests
    for (let i = 0; i < 110; i++) {
      const result = await rateLimit(ip);
      if (i >= 100) {
        expect(result.success).toBe(false);
      }
    }
  });
});
```

## Próximos Passos

### Fase 1: Setup Base
1. ✅ Configurar tRPC
2. ⏳ Implementar routers base
3. ❌ Adicionar validação

### Fase 2: Segurança
1. ⏳ Rate limiting
2. ❌ Autenticação
3. ❌ Logging

### Fase 3: Monitoramento
1. ❌ Métricas
2. ❌ Alertas
3. ❌ Dashboards

## Notas Técnicas
1. Manter tipos atualizados
2. Documentar mudanças
3. Testar endpoints
4. Monitorar performance 