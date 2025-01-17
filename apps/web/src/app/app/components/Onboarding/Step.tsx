import React from 'react';

interface StepProps {
    title: string;
    description: string;
    isActive: boolean;
    isCompleted: boolean;
}

export const Step: React.FC<StepProps> = ({
    title,
    description,
    isActive,
    isCompleted
}) => {
    return (
        <div className={`p-4 border rounded ${isActive ? 'border-blue-500' : ''}`}>
            <h3 className="font-medium">
                {isCompleted ? '✓ ' : ''}{title}
            </h3>
            <p className="text-gray-600">{description}</p>
        </div>
    );
}; 