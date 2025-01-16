import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfills necessários para Next.js
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Configuração de variáveis de ambiente para testes
Object.defineProperty(process.env, 'NEXT_PUBLIC_APP_URL', { value: 'http://localhost:3001' });
Object.defineProperty(process.env, 'NODE_ENV', { value: 'test' });

// Limpar todos os mocks após cada teste
afterEach(() => {
  jest.clearAllMocks();
});

// Configuração global de timeout
jest.setTimeout(10000); 