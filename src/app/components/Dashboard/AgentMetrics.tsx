import React from 'react';

interface Metric {
    id: string;
    name: string;
    value: number;
    trend: 'up' | 'down' | 'stable';
}

export const AgentMetrics: React.FC<{
    metrics: Metric[];
}> = ({ metrics }) => {
    return (
        <div className="grid grid-cols-3 gap-4">
            {metrics.map((metric) => (
                <div key={metric.id} className="p-4 border rounded">
                    <h3 className="font-medium">{metric.name}</h3>
                    <p className="text-2xl">{metric.value}</p>
                    <span className={`text-${metric.trend === 'up' ? 'green' : 'red'}-500`}>
                        {metric.trend === 'up' ? '↑' : '↓'}
                    </span>
                </div>
            ))}
        </div>
    );
}; 