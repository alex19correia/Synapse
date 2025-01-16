export interface LogMetricsData {
  level: string
  component: string
  hasError: boolean
  metadata?: Record<string, unknown>
}

export interface ApiMetricsData {
  path: string
  method: string
  statusCode: number
  duration: number
}

export class MetricsCollector {
  static track_llm_request(model: string, duration: number, tokens: number, success: boolean): void
  static track_cache_operation(operation_type: string, hit: boolean): void
  static track_user_activity(user_id: string, session_duration: number): void
  static update_memory_usage(component: string, usage: number): void
  static track_error(error_type: string, component: string): void
  static track_log(data: LogMetricsData): void
  static track_api_request(data: ApiMetricsData): void
  static track_duration(component: string, duration: number): void
} 