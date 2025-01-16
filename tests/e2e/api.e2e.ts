import { test, expect } from '@playwright/test';

test.describe('API Tests', () => {
  test.beforeEach(async ({ request }) => {
    // Reset any test data if needed
    const response = await request.post('/api/test/reset');
    expect(response.ok()).toBeTruthy();
  });

  test('health check returns ok', async ({ request }) => {
    const response = await request.get('/api/health');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toEqual({ status: 'ok' });
  });

  test('protected endpoints require authentication', async ({ request }) => {
    // Test protected endpoints
    const protectedEndpoints = [
      '/api/user/profile',
      '/api/dashboard/stats',
      '/api/settings'
    ];

    for (const endpoint of protectedEndpoints) {
      const response = await request.get(endpoint);
      expect(response.status()).toBe(401);
    }
  });

  test('rate limiting works', async ({ request }) => {
    // Make multiple requests in quick succession
    const requests = Array(10).fill('/api/test/rate-limit').map(
      endpoint => request.get(endpoint)
    );
    
    const responses = await Promise.all(requests);
    const tooManyRequests = responses.some(r => r.status() === 429);
    expect(tooManyRequests).toBeTruthy();
  });

  test('CORS headers are set correctly', async ({ request }) => {
    const response = await request.get('/api/health', {
      headers: {
        'Origin': 'http://localhost:3001'
      }
    });
    
    expect(response.headers()['access-control-allow-origin']).toBeTruthy();
  });

  test('invalid endpoints return 404', async ({ request }) => {
    const response = await request.get('/api/non-existent-endpoint');
    expect(response.status()).toBe(404);
  });

  test('malformed requests return 400', async ({ request }) => {
    const response = await request.post('/api/user/profile', {
      data: { invalidField: true }
    });
    expect(response.status()).toBe(400);
  });
}); 