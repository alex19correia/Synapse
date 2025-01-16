import { NextRequest } from 'next/server'
import { securityHeadersMiddleware } from '../middleware/security-headers'

describe('Security Headers Middleware', () => {
  it('should add all required security headers', () => {
    // Mock request
    const request = new NextRequest(new Request('https://example.com'))
    
    // Get response with security headers
    const response = securityHeadersMiddleware(request)
    
    // Verify required headers
    const requiredHeaders = [
      'Content-Security-Policy',
      'X-DNS-Prefetch-Control',
      'X-Frame-Options',
      'Strict-Transport-Security',
      'X-Content-Type-Options',
      'X-XSS-Protection',
      'Referrer-Policy',
      'Permissions-Policy'
    ]

    requiredHeaders.forEach(header => {
      expect(response.headers.get(header)).toBeTruthy()
    })

    // Verify specific header values
    expect(response.headers.get('X-Frame-Options')).toBe('DENY')
    expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff')
    expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block')
    expect(response.headers.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin')
  })

  it('should have correct CSP directives', () => {
    const request = new NextRequest(new Request('https://example.com'))
    const response = securityHeadersMiddleware(request)
    
    const csp = response.headers.get('Content-Security-Policy')
    expect(csp).toBeTruthy()
    
    // Verify essential CSP directives
    expect(csp).toContain("default-src 'self'")
    expect(csp).toContain("script-src")
    expect(csp).toContain("style-src")
    expect(csp).toContain("object-src 'none'")
    expect(csp).toContain("base-uri 'self'")
    expect(csp).toContain("frame-ancestors 'none'")
  })
}) 