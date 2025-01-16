import React from 'react';

interface Suggestion {
    id: string;
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
}

export const ImprovementSuggestions: React.FC<{
    suggestions: Suggestion[];
}> = ({ suggestions }) => {
    return (
        <div className="space-y-4">
            {suggestions.map((suggestion) => (
                <div key={suggestion.id} className="p-4 border rounded">
                    <h3 className="font-medium">{suggestion.title}</h3>
                    <p className="text-gray-600">{suggestion.description}</p>
                    <span className={`text-${suggestion.priority}-500`}>
                        {suggestion.priority} priority
                    </span>
                </div>
            ))}
        </div>
    );
}; 