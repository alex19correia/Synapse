import { useState, useEffect } from 'react';
import posthog from 'posthog-js';

interface Metrics {
  success_rate: number;
  response_time: number;
  usage_count: number;
}

type TimeframeType = 'day' | 'week' | 'month';

export function useAnalytics() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [timeframe, setTimeframe] = useState<TimeframeType>('day');

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      // Simular dados por enquanto
      setMetrics({
        success_rate: 85,
        response_time: 250,
        usage_count: 1200
      });
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [timeframe]);

  return {
    metrics,
    loading,
    error,
    timeframe,
    setTimeframe,
    trackEvent: (name: string, properties?: Record<string, any>) => {
      posthog.capture(name, properties);
    },
    trackWorkflowStart: (workflowId: string) => {
      posthog.capture('workflow_started', { workflowId });
    },
    trackWorkflowComplete: (workflowId: string, progress: number) => {
      posthog.capture('workflow_completed', { workflowId, progress });
    }
  };
} 