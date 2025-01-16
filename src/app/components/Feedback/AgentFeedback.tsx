import React from 'react';
import { useFeedbackSystem } from '@/app/hooks/useFeedbackSystem';
import { Rating } from './Rating';
import { FeedbackForm } from './FeedbackForm';

export const AgentFeedback: React.FC<{
    agentId: string;
    responseId: string;
}> = ({ agentId, responseId }) => {
    const { submitFeedback, feedbackStats } = useFeedbackSystem(agentId);

    return (
        <div className="space-y-4">
            <Rating
                value={feedbackStats.rating}
                onChange={async (rating) => {
                    await submitFeedback({
                        agentId,
                        responseId,
                        type: 'rating',
                        value: rating
                    });
                }}
            />
            
            <FeedbackForm
                onSubmit={async (feedback) => {
                    await submitFeedback({
                        agentId,
                        responseId,
                        type: 'detailed',
                        value: feedback.feedback
                    });
                }}
            />
        </div>
    );
}; 
