import React from 'react';
import { Rating } from './Rating';

interface FeedbackFormProps {
    onSubmit: (data: { rating: number; feedback: string }) => Promise<void>;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({ onSubmit }) => {
    const [rating, setRating] = React.useState(0);
    const [feedback, setFeedback] = React.useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await onSubmit({ rating, feedback });
        setRating(0);
        setFeedback('');
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label>Rating</label>
                <Rating value={rating} onChange={setRating} />
            </div>
            <div>
                <label>Feedback</label>
                <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    className="w-full p-2 border rounded"
                />
            </div>
            <button type="submit" className="btn btn-primary">
                Submit Feedback
            </button>
        </form>
    );
}; 