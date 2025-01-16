import { redis } from '../lib/redis'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createLogger } from '../services/logger'

// Configurações de Rate Limit
const WINDOW_SIZE = 60 // 1 minuto
const MAX_REQUESTS = 100 // máximo de requisições por minuto
const BLOCK_DURATION = 300 // 5 minutos de bloqueio após exceder limite

// Lista de IPs bloqueados temporariamente
const BLOCKED_KEY_PREFIX = 'rate-limit:blocked:'

// Cria uma instância do logger para rate limiting
const logger = createLogger({ 
  minLevel: 'info',
  component: 'rate-limit'
})

export async function rateLimitMiddleware(request: NextRequest) {
  const forwarded = request.headers.get('x-forwarded-for')
  const ip = forwarded ? forwarded.split(',')[0].trim() : '127.0.0.1'
  const key = `rate-limit:${ip}`
  const blockedKey = `${BLOCKED_KEY_PREFIX}${ip}`

  try {
    // Log da requisição
    logger.request(request, { ip })

    // Verifica se o IP está bloqueado
    const isBlocked = await redis.get(blockedKey)
    if (isBlocked) {
      const ttl = await redis.ttl(blockedKey)
      logger.warn('IP blocked', { ip, ttl })
      return new NextResponse('IP Temporarily Blocked', {
        status: 403,
        headers: {
          'Retry-After': ttl.toString(),
          'X-RateLimit-Reset': (Date.now() + ttl * 1000).toString(),
        },
      })
    }

    // Incrementa o contador para o IP
    const requests = await redis.incr(key)

    // Se é a primeira requisição, define o TTL
    if (requests === 1) {
      await redis.expire(key, WINDOW_SIZE)
    }

    // Verifica se excedeu o limite
    if (requests > MAX_REQUESTS) {
      // Bloqueia o IP por BLOCK_DURATION segundos
      await redis.setex(blockedKey, BLOCK_DURATION, '1')
      
      logger.warn('Rate limit exceeded', { ip, requests })
      return new NextResponse('Too Many Requests', {
        status: 429,
        headers: {
          'Retry-After': BLOCK_DURATION.toString(),
          'X-RateLimit-Reset': (Date.now() + BLOCK_DURATION * 1000).toString(),
        },
      })
    }

    // Adiciona headers de rate limit
    const response = NextResponse.next()
    const remaining = MAX_REQUESTS - requests
    const reset = await redis.ttl(key)

    response.headers.set('X-RateLimit-Limit', MAX_REQUESTS.toString())
    response.headers.set('X-RateLimit-Remaining', remaining.toString())
    response.headers.set('X-RateLimit-Reset', (Date.now() + reset * 1000).toString())
    
    // Adiciona header de aviso quando estiver próximo do limite
    if (remaining < MAX_REQUESTS * 0.1) { // 10% restante
      logger.warn('Rate limit warning', { ip, remaining })
      response.headers.set('X-RateLimit-Warning', 'true')
    }

    return response
  } catch (error) {
    logger.exception(error as Error, { ip })
    // Em caso de erro, permite a requisição mas com header de aviso
    const response = NextResponse.next()
    response.headers.set('X-RateLimit-Error', 'true')
    return response
  }
} 