/// <reference types="next" />
import type { NextRequest } from 'next/server'
import { rateLimitMiddleware } from './middleware/rate-limit'
import { securityHeadersMiddleware } from './middleware/security-headers'

export async function middleware(request: NextRequest) {
  // Aplica headers de segurança em todas as rotas
  const securityResponse = securityHeadersMiddleware(request)

  // Aplica rate limiting apenas em rotas da API
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const rateLimitResponse = await rateLimitMiddleware(request)
    
    // Copia os headers de segurança para a resposta do rate limit
    securityResponse.headers.forEach((value, key) => {
      rateLimitResponse.headers.set(key, value)
    })
    
    return rateLimitResponse
  }

  return securityResponse
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
} 