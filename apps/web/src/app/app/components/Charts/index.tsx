'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export interface Metric {
  timestamp: string;
  value: number;
  label: string;
}

interface ChartProps {
  metrics: Metric[];
}

export function MetricsChart({ metrics }: ChartProps) {
  return (
    <div className="w-full h-[300px]">
      <LineChart width={600} height={300} data={metrics}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
    </div>
  );
} 