import { createLogger } from '../services/logger'
import { MetricsCollector } from '../lib/metrics'

// Mock do MetricsCollector
jest.mock('../lib/metrics', () => ({
  MetricsCollector: {
    track_log: jest.fn().mockResolvedValue(undefined),
    track_error: jest.fn().mockResolvedValue(undefined),
    track_duration: jest.fn().mockResolvedValue(undefined),
    track_api_request: jest.fn().mockResolvedValue(undefined)
  }
}))

describe('Logger Service', () => {
  let consoleInfoSpy: jest.SpyInstance
  let consoleWarnSpy: jest.SpyInstance
  let consoleErrorSpy: jest.SpyInstance

  beforeEach(() => {
    consoleInfoSpy = jest.spyOn(console, 'info').mockImplementation()
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation()
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()
    jest.clearAllMocks()
  })

  afterEach(() => {
    consoleInfoSpy.mockRestore()
    consoleWarnSpy.mockRestore()
    consoleErrorSpy.mockRestore()
  })

  it('should log info messages and track metrics', async () => {
    const logger = createLogger({ 
      prettyPrint: false,
      component: 'test-component'
    })
    const message = 'Test info message'
    const metadata = { test: 'data' }
    
    await logger.info(message, metadata)
    
    // Verifica o log
    expect(consoleInfoSpy).toHaveBeenCalled()
    const loggedData = JSON.parse(consoleInfoSpy.mock.calls[0][0])
    expect(loggedData).toMatchObject({
      level: 'info',
      message,
      metadata,
      component: 'test-component'
    })

    // Verifica as métricas
    expect(MetricsCollector.track_log).toHaveBeenCalledWith({
      level: 'info',
      component: 'test-component',
      hasError: false,
      metadata
    })
  })

  it('should log warning messages and track metrics', async () => {
    const logger = createLogger({ 
      prettyPrint: false,
      component: 'test-component'
    })
    const message = 'Test warning message'
    
    await logger.warn(message)
    
    // Verifica o log
    expect(consoleWarnSpy).toHaveBeenCalled()
    const loggedData = JSON.parse(consoleWarnSpy.mock.calls[0][0])
    expect(loggedData).toMatchObject({
      level: 'warn',
      message,
      component: 'test-component'
    })

    // Verifica as métricas
    expect(MetricsCollector.track_log).toHaveBeenCalledWith({
      level: 'warn',
      component: 'test-component',
      hasError: false,
      metadata: undefined
    })
  })

  it('should log error messages and track error metrics', async () => {
    const logger = createLogger({ 
      prettyPrint: false,
      component: 'test-component'
    })
    const error = new Error('Test error')
    
    await logger.exception(error)
    
    // Verifica o log
    expect(consoleErrorSpy).toHaveBeenCalled()
    const loggedData = JSON.parse(consoleErrorSpy.mock.calls[0][0])
    expect(loggedData).toMatchObject({
      level: 'error',
      message: 'Exception occurred',
      component: 'test-component',
      metadata: {
        name: error.name,
        message: error.message
      }
    })

    // Verifica as métricas
    expect(MetricsCollector.track_log).toHaveBeenCalledWith({
      level: 'error',
      component: 'test-component',
      hasError: true,
      metadata: expect.any(Object)
    })
    expect(MetricsCollector.track_error).toHaveBeenCalledWith('log_error', 'test-component')
  })

  it('should track API metrics when logging API requests', async () => {
    const logger = createLogger({ 
      prettyPrint: false,
      component: 'test-component'
    })
    
    await logger.api('/test', 'GET', 200, 0.123, { userId: '123' })
    
    // Verifica o log
    expect(consoleInfoSpy).toHaveBeenCalled()
    const loggedData = JSON.parse(consoleInfoSpy.mock.calls[0][0])
    expect(loggedData).toMatchObject({
      level: 'info',
      message: 'API request completed',
      component: 'test-component',
      metadata: {
        path: '/test',
        method: 'GET',
        statusCode: 200,
        duration: 0.123,
        userId: '123'
      }
    })

    // Verifica as métricas
    expect(MetricsCollector.track_api_request).toHaveBeenCalledWith({
      path: '/test',
      method: 'GET',
      statusCode: 200,
      duration: 0.123
    })
    expect(MetricsCollector.track_duration).toHaveBeenCalledWith('test-component', 0.123)
  })

  it('should format logs correctly in pretty print mode', async () => {
    const logger = createLogger({ 
      prettyPrint: true,
      component: 'test-component'
    })
    const message = 'Test message'
    
    await logger.info(message)
    
    expect(consoleInfoSpy).toHaveBeenCalled()
    const loggedMessage = consoleInfoSpy.mock.calls[0][0]
    expect(loggedMessage).toMatch(/\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z\] INFO: Test message/)
  })

  it('should handle metric tracking errors gracefully', async () => {
    const logger = createLogger({ 
      prettyPrint: false,
      component: 'test-component'
    })
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()
    
    // Simula erro no tracking
    const error = new Error('Metric tracking failed')
    jest.spyOn(MetricsCollector, 'track_log').mockRejectedValueOnce(error)
    
    // Não deve falhar ao logar
    await expect(logger.info('test')).resolves.not.toThrow()
    
    // Deve logar o erro
    expect(consoleErrorSpy).toHaveBeenCalledWith(error)
  })
}) 