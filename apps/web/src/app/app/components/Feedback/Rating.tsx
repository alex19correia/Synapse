import React from 'react';

interface RatingProps {
    value: number;
    onChange: (value: number) => void;
}

export const Rating: React.FC<RatingProps> = ({ value, onChange }) => {
    return (
        <div className="flex space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    onClick={() => onChange(star)}
                    className={`text-2xl ${
                        star <= value ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                >
                    ★
                </button>
            ))}
        </div>
    );
}; 