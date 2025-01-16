export * from '@/app/components/Charts'; 

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export interface Metric {
  timestamp: string;
  value: number;
  label: string;
}

export interface ChartProps {
  metrics: Metric[];
}

export function MetricsChart({ metrics }: ChartProps) {
  return (
    <LineChart width={600} height={300} data={metrics}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
} 