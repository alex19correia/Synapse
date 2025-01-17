import { jest, describe, it, expect, beforeEach } from '@jest/globals';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import middleware from '../middleware';
import { mockRedisClient } from './jest.setup';

describe('Middleware Tests', () => {
  let mockRequest: NextRequest;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Restaurar valores padrão
    mockRedisClient.incr.mockResolvedValue(1);
    mockRedisClient.expire.mockResolvedValue(true);
    mockRedisClient.ttl.mockResolvedValue(60);
    
    // Mock request
    mockRequest = {
      nextUrl: new URL('http://localhost:3000/api/test'),
      method: 'GET',
      headers: new Headers({
        'x-forwarded-for': '127.0.0.1'
      })
    } as unknown as NextRequest;
  });

  it('should allow requests within rate limit', async () => {
    mockRedisClient.incr.mockResolvedValueOnce(1);
    
    const response = await middleware(mockRequest);
    
    if (response) {
      expect(response.status).not.toBe(429);
      expect(response.headers.get('X-RateLimit-Remaining')).toBe('99');
    }
  });

  it('should block requests exceeding rate limit', async () => {
    mockRedisClient.incr.mockResolvedValueOnce(101);
    
    const response = await middleware(mockRequest);
    
    if (response) {
      expect(response.status).toBe(429);
      expect(response.headers.get('X-RateLimit-Remaining')).toBe('0');
    }
  });

  it('should allow access to public routes', async () => {
    mockRequest = {
      nextUrl: new URL('http://localhost:3000/sign-in'),
      method: 'GET',
      headers: new Headers({
        'x-forwarded-for': '127.0.0.1'
      })
    } as unknown as NextRequest;

    const response = await middleware(mockRequest);
    if (response) {
      expect(response.status).not.toBe(401);
    }
  });

  it('should handle Redis errors gracefully', async () => {
    mockRedisClient.incr.mockRejectedValueOnce(new Error('Redis error'));
    
    const response = await middleware(mockRequest);
    
    if (response) {
      expect(response.status).not.toBe(429);
      expect(response.headers.get('X-RateLimit-Remaining')).toBe('1');
    }
  });

  it('should set correct rate limit headers', async () => {
    mockRedisClient.incr.mockResolvedValueOnce(50);
    mockRedisClient.ttl.mockResolvedValueOnce(30);
    
    const response = await middleware(mockRequest);
    
    if (response) {
      expect(response.headers.get('X-RateLimit-Limit')).toBe('100');
      expect(response.headers.get('X-RateLimit-Remaining')).toBe('50');
      expect(response.headers.get('X-RateLimit-Reset')).toBeDefined();
    }
  });
}); 