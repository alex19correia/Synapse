# Testes do Middleware

## Visão Geral
O middleware da aplicação é responsável por duas funcionalidades principais:
1. Autenticação usando Clerk
2. Rate limiting usando Upstash Redis

## Estrutura dos Testes

### Testes Automatizados (Jest)
Localização: `src/tests/middleware.test.ts`

Os testes automatizados cobrem os seguintes cenários:

1. **Rate Limiting**
   - Permite requisições dentro do limite
   - Bloqueia requisições que excedem o limite
   - Define corretamente os headers de rate limit
   - Lida graciosamente com erros do Redis

2. **Autenticação**
   - Permite acesso a rotas públicas
   - Requer autenticação para rotas protegidas
   - Valida tokens JWT

### Testes Manuais
Localização: `src/scripts/test-middleware.ts`

Script para testar o middleware em um ambiente real:

1. **Teste de Rota Não Autenticada**
   - Tenta acessar rota protegida sem autenticação
   - Espera receber erro 401

2. **Teste de Rate Limiting**
   - Envia múltiplas requisições em paralelo
   - Verifica se o rate limiting é ativado após exceder o limite

3. **Teste de Autenticação**
   - Tenta acessar rota protegida com token válido
   - Verifica se a requisição é bem-sucedida

## Testes do Middleware de Métricas

### Testes Automatizados
Localização: `src/tests/metrics-middleware.test.ts`

1. **Rate Limiting de Métricas**
```typescript
describe('Metrics Rate Limiting', () => {
  test('permite métricas dentro do limite', async () => {
    const response = await request(app)
      .post('/api/metrics/llm')
      .send({
        model: 'gpt-4',
        duration: 1.5,
        tokens: 150,
        success: true
      });
    
    expect(response.status).toBe(200);
    expect(response.headers['x-ratelimit-remaining']).toBeDefined();
  });

  test('bloqueia métricas que excedem o limite', async () => {
    // Configurar limite baixo para teste
    await redis.set('metrics:limit:test', '1');
    
    // Primeira requisição (permitida)
    const response1 = await request(app)
      .post('/api/metrics/test')
      .send({});
    expect(response1.status).toBe(200);
    
    // Segunda requisição (bloqueada)
    const response2 = await request(app)
      .post('/api/metrics/test')
      .send({});
    expect(response2.status).toBe(429);
    expect(response2.headers['retry-after']).toBeDefined();
  });
});

describe('Batch Processing', () => {
  test('valida tamanho do batch', async () => {
    const response = await request(app)
      .post('/api/metrics/batch')
      .send([{ type: 'test', data: {} }])
      .set('X-Batch-Size', '2');  // Tamanho incorreto
    
    expect(response.status).toBe(400);
    expect(response.body.error).toContain('Batch size mismatch');
  });

  test('processa batch válido', async () => {
    const batch = [
      { type: 'test', data: { value: 1 } },
      { type: 'test', data: { value: 2 } }
    ];

    const response = await request(app)
      .post('/api/metrics/batch')
      .send(batch)
      .set('X-Batch-Size', '2');
    
    expect(response.status).toBe(200);
    expect(response.body.processed).toBe(2);
  });
});

### Testes Manuais
Localização: `src/scripts/test-metrics.ts`

Script para testar o middleware de métricas em ambiente real:

1. **Teste de Rate Limiting**
```typescript
async function testRateLimiting() {
  console.log('Testando rate limiting de métricas...');
  
  const metric = {
    type: 'test',
    data: { value: 1 }
  };
  
  // Enviar métricas até atingir limite
  let count = 0;
  while (true) {
    const response = await fetch('http://localhost:3000/api/metrics/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metric)
    });
    
    if (response.status === 429) {
      console.log(`Rate limit atingido após ${count} requisições`);
      console.log(`Retry-After: ${response.headers.get('retry-after')}s`);
      break;
    }
    
    count++;
  }
}
```

2. **Teste de Batch Processing**
```typescript
async function testBatchProcessing() {
  console.log('Testando processamento em batch...');
  
  const batch = Array.from({ length: 50 }, (_, i) => ({
    type: 'test',
    data: { value: i }
  }));
  
  const response = await fetch('http://localhost:3000/api/metrics/batch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Batch-Size': '50'
    },
    body: JSON.stringify(batch)
  });
  
  console.log('Status:', response.status);
  console.log('Resultado:', await response.json());
}
```

### Como Executar
```bash
# Testes automatizados
npm run test:metrics-middleware

# Testes manuais
npm run test:metrics-manual
```

## Mocks
Os testes automatizados utilizam mocks para:
- Cliente Redis (`src/tests/jest.setup.ts`)
- Autenticação Clerk
- Requisições HTTP

## Cobertura de Testes
Os testes cobrem:
- ✅ Rate limiting
- ✅ Autenticação
- ✅ Headers de resposta
- ✅ Tratamento de erros
- ✅ Rotas públicas vs protegidas
- ✅ Rate limiting de métricas
- ✅ Processamento em batch
- ✅ Validação de métricas 