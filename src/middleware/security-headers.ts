import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createLogger } from '../services/logger'

// Cria uma instância do logger para security headers
const logger = createLogger({ 
  minLevel: 'info',
  component: 'security-headers'
})

export function securityHeadersMiddleware(request: NextRequest) {
  try {
    logger.request(request, { middleware: 'security-headers' })
    
    const response = NextResponse.next()

    // Content Security Policy
    const cspHeader = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.clerk.dev https://va.vercel-scripts.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https: blob:",
      "font-src 'self' https://fonts.gstatic.com",
      "frame-src 'self' https://clerk.alexandrecorreia.pt",
      "connect-src 'self' https://api.alexandrecorreia.pt https://va.vercel-analytics.com https://vitals.vercel-insights.com",
      "media-src 'self'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests"
    ].join('; ')

    // Security Headers
    const headers = {
      'Content-Security-Policy': cspHeader,
      'X-DNS-Prefetch-Control': 'on',
      'X-Frame-Options': 'DENY',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), interest-cohort=()'
    }

    // Adiciona os headers de segurança
    Object.entries(headers).forEach(([key, value]) => {
      response.headers.set(key, value)
    })

    logger.info('Security headers added', { 
      url: request.url,
      headers: Object.keys(headers)
    })

    return response
  } catch (error) {
    logger.exception(error as Error, { url: request.url })
    return NextResponse.next()
  }
} 