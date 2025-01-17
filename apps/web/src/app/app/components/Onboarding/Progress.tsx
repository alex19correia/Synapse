import React from 'react';

interface ProgressProps {
    value: number;
    total: number;
}

export const Progress: React.FC<ProgressProps> = ({ value, total }) => {
    const percentage = (value / total) * 100;
    
    return (
        <div className="w-full bg-gray-200 rounded">
            <div
                className="bg-blue-500 rounded h-2"
                style={{ width: `${percentage}%` }}
            />
        </div>
    );
}; 