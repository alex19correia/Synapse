# Sistema de Logging

## Visão Geral
```python
logging_system = {
    "framework": "Winston",
    "storage": "Local Files",
    "status": "planned",
    "features": [
        "Structured Logging",
        "Error Tracking",
        "Performance Metrics",
        "Audit Trail"
    ],
    "integrations": {
        "monitoring": "Grafana",
        "alerts": "Email/Slack"
    }
}
```

## Componentes Principais

### 1. Logger Base
```typescript
// src/lib/logger/base.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'synapse-assistant',
    environment: process.env.NODE_ENV
  },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: 'logs/combined.log'
    })
  ]
});
```

### 2. Categorias
```typescript
// src/lib/logger/categories.ts
export const loggers = {
  api: logger.child({ category: 'api' }),
  auth: logger.child({ category: 'auth' }),
  llm: logger.child({ category: 'llm' }),
  system: logger.child({ category: 'system' })
};

export const errorLogger = logger.child({
  level: 'error',
  category: 'error'
});

export const auditLogger = logger.child({
  category: 'audit',
  persist: true
});
```

### 3. Formatação
```typescript
// src/lib/logger/formats.ts
export const logFormats = {
  detailed: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
    winston.format.prettyPrint()
  ),
  
  simple: winston.format.combine(
    winston.format.simple(),
    winston.format.colorize()
  ),
  
  audit: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      return JSON.stringify({
        timestamp,
        level,
        message,
        ...meta
      });
    })
  )
};
```

## Implementação

### 1. API Logging
```typescript
// src/middleware.ts
export async function middleware(req: NextRequest) {
  const start = Date.now();
  const response = await NextResponse.next();
  const duration = Date.now() - start;
  
  loggers.api.info('API Request', {
    method: req.method,
    path: req.url,
    status: response.status,
    duration,
    ip: req.ip
  });
  
  return response;
}
```

### 2. Error Tracking
```typescript
// src/lib/logger/error.ts
export const errorTracker = {
  capture: (error: Error, context: object = {}) => {
    errorLogger.error(error.message, {
      stack: error.stack,
      ...context
    });
  },
  
  warn: (message: string, context: object = {}) => {
    errorLogger.warn(message, context);
  },
  
  fatal: (error: Error, context: object = {}) => {
    errorLogger.error('FATAL ERROR', {
      message: error.message,
      stack: error.stack,
      ...context
    });
    
    // Notify team
    notifyTeam('FATAL ERROR', error);
  }
};
```

### 3. Audit Trail
```typescript
// src/lib/logger/audit.ts
export const auditTrail = {
  user: (action: string, userId: string, details: object = {}) => {
    auditLogger.info(`User Action: ${action}`, {
      userId,
      action,
      ...details
    });
  },
  
  system: (action: string, details: object = {}) => {
    auditLogger.info(`System Action: ${action}`, {
      action,
      ...details
    });
  },
  
  security: (event: string, details: object = {}) => {
    auditLogger.info(`Security Event: ${event}`, {
      event,
      ...details
    });
  }
};
```

## Monitoramento

### 1. Métricas
```typescript
// src/lib/logger/metrics.ts
export const loggingMetrics = {
  logVolume: new Counter({
    name: 'log_entries_total',
    help: 'Total number of log entries',
    labelNames: ['level', 'category']
  }),
  
  errorRate: new Counter({
    name: 'error_logs_total',
    help: 'Total number of error logs'
  }),
  
  logSize: new Gauge({
    name: 'log_size_bytes',
    help: 'Size of log files in bytes'
  })
};
```

### 2. Alertas
```typescript
// src/lib/logger/alerts.ts
export const alertConfig = {
  thresholds: {
    errors: {
      warning: 10, // per minute
      critical: 50 // per minute
    },
    logSize: {
      warning: 100 * 1024 * 1024, // 100MB
      critical: 500 * 1024 * 1024 // 500MB
    }
  },
  channels: {
    email: ['team@synapse.ai'],
    slack: '#alerts'
  }
};
```

## Retenção

### 1. Rotação
```typescript
// src/lib/logger/rotation.ts
export const rotationConfig = {
  maxSize: '100m',
  maxFiles: '14d',
  compress: true,
  datePattern: 'YYYY-MM-DD',
  dirname: 'logs',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  )
};
```

### 2. Limpeza
```typescript
// src/lib/logger/cleanup.ts
export const cleanupConfig = {
  retention: {
    error: '90d',
    audit: '365d',
    general: '30d'
  },
  schedule: '0 0 * * *', // Daily at midnight
  compress: {
    enabled: true,
    age: '7d'
  }
};
```

## Próximos Passos

### Fase 1: Setup Base
1. ✅ Configuração Winston
2. ⏳ Categorias de log
3. ❌ Rotação de arquivos

### Fase 2: Monitoramento
1. ❌ Métricas de logging
2. ❌ Alertas
3. ❌ Dashboard

### Fase 3: Otimização
1. ❌ Compressão
2. ❌ Indexação
3. ❌ Busca

## Notas Técnicas
1. Monitorar tamanho dos logs
2. Implementar rotação
3. Definir retenção
4. Estruturar mensagens 