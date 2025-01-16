import { NextRequest } from 'next/server'
import { MetricsCollector } from '../lib/metrics'

// Níveis de log
export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

// Interface para dados adicionais do log
interface LogMetadata {
  [key: string]: unknown
}

// Interface para o log estruturado
interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  metadata?: LogMetadata
  component?: string
}

// Interface de configuração
export interface LoggerConfig {
  minLevel: LogLevel
  prettyPrint: boolean
  component?: string
}

// Configuração padrão
const defaultConfig: LoggerConfig = {
  minLevel: (process.env.LOG_LEVEL as LogLevel) || 'info',
  prettyPrint: process.env.NODE_ENV === 'development',
}

// Função para formatar o log
function formatLog(entry: LogEntry, config: LoggerConfig): string {
  if (config.prettyPrint) {
    return `[${entry.timestamp}] ${entry.level.toUpperCase()}: ${entry.message} ${
      entry.metadata ? JSON.stringify(entry.metadata, null, 2) : ''
    }`
  }
  return JSON.stringify(entry)
}

// Função para trackear métricas baseadas no log
async function trackMetrics(entry: LogEntry) {
  const component = entry.component || 'unknown'
  
  // Incrementa contador de logs por nível e componente
  await MetricsCollector.track_log({
    level: entry.level,
    component,
    hasError: entry.level === 'error',
    metadata: entry.metadata
  })

  // Se for erro, incrementa também o contador de erros
  if (entry.level === 'error') {
    await MetricsCollector.track_error('log_error', component)
  }

  // Se tiver informação de latência nos metadados, registra
  if (entry.metadata?.duration) {
    await MetricsCollector.track_duration(component, entry.metadata.duration as number)
  }
}

// Função principal de logging
async function log(level: LogLevel, message: string, metadata?: LogMetadata, config: LoggerConfig = defaultConfig) {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    metadata,
    component: config.component
  }

  // Escreve o log no formato apropriado
  const formattedLog = formatLog(entry, config)
  
  // Envia métricas (não aguarda para não bloquear)
  trackMetrics(entry).catch(console.error)
  
  switch (level) {
    case 'debug':
      console.debug(formattedLog)
      break
    case 'info':
      console.info(formattedLog)
      break
    case 'warn':
      console.warn(formattedLog)
      break
    case 'error':
      console.error(formattedLog)
      break
  }
}

// Criador de logger
export function createLogger(config: Partial<LoggerConfig> = {}) {
  const finalConfig: LoggerConfig = { ...defaultConfig, ...config }

  return {
    debug: (message: string, metadata?: LogMetadata) => log('debug', message, metadata, finalConfig),
    info: (message: string, metadata?: LogMetadata) => log('info', message, metadata, finalConfig),
    warn: (message: string, metadata?: LogMetadata) => log('warn', message, metadata, finalConfig),
    error: (message: string, metadata?: LogMetadata) => log('error', message, metadata, finalConfig),
    
    // Função específica para logs de request
    request: (req: NextRequest, metadata?: LogMetadata) => {
      const requestMetadata = {
        method: req.method,
        url: req.url,
        headers: Object.fromEntries(req.headers),
        ...metadata,
      }
      return log('info', 'Incoming request', requestMetadata, finalConfig)
    },

    // Função específica para logs de API
    api: async (path: string, method: string, statusCode: number, duration: number, metadata?: LogMetadata) => {
      const apiMetadata = {
        path,
        method,
        statusCode,
        duration,
        ...metadata,
      }
      await log('info', 'API request completed', apiMetadata, finalConfig)

      // Registra métricas específicas de API (não aguarda para não bloquear)
      MetricsCollector.track_api_request({
        path,
        method,
        statusCode,
        duration
      }).catch(console.error)
    },

    // Função específica para logs de erro
    exception: (error: Error, metadata?: LogMetadata) => {
      const errorMetadata = {
        name: error.name,
        message: error.message,
        stack: error.stack,
        ...metadata,
      }
      return log('error', 'Exception occurred', errorMetadata, finalConfig)
    }
  }
}

// Exporta uma instância padrão do logger
export const logger = createLogger() 