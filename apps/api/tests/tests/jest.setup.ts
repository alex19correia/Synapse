import { jest } from '@jest/globals';

// Mock do Redis
const mockRedisClient = {
  connect: jest.fn().mockImplementation(async () => {}),
  isOpen: true,
  on: jest.fn(),
  incr: jest.fn().mockImplementation(async () => 1),
  expire: jest.fn().mockImplementation(async () => true),
  ttl: jest.fn().mockImplementation(async () => 60),
  quit: jest.fn().mockImplementation(async () => {})
} as any;

jest.mock('redis', () => ({
  createClient: jest.fn().mockReturnValue(mockRedisClient)
}));

// Exportar o mock para uso nos testes
export { mockRedisClient };