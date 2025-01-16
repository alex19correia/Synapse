'use client';

import { useEffect } from 'react';
import { MetricsChart, Metric } from '../Charts/MetricsChart';
import { useAnalytics } from '@/app/hooks/useAnalytics';

interface AgentPerformanceProps {
  agentId: string;
}

export function AgentPerformance({ agentId }: AgentPerformanceProps) {
  const { metrics, loading, error, timeframe, setTimeframe, trackEvent } = useAnalytics();

  useEffect(() => {
    trackEvent('agent_view', { agentId });
  }, [agentId, trackEvent]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!metrics) return null;

  const chartData: Metric[] = [
    {
      timestamp: new Date().toISOString(),
      value: metrics.success_rate,
      label: 'Success Rate'
    },
    {
      timestamp: new Date().toISOString(),
      value: metrics.response_time,
      label: 'Response Time'
    },
    {
      timestamp: new Date().toISOString(),
      value: metrics.usage_count,
      label: 'Usage Count'
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Agent Performance</h3>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value as 'day' | 'week' | 'month')}
          className="bg-gray-700 rounded-md px-2 py-1"
        >
          <option value="day">Last 24 hours</option>
          <option value="week">Last 7 days</option>
          <option value="month">Last 30 days</option>
        </select>
      </div>
      <MetricsChart metrics={chartData} />
    </div>
  );
} 