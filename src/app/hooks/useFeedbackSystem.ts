import { useState } from 'react';

interface FeedbackStats {
  rating: number;
}

interface FeedbackData {
  agentId: string;
  responseId: string;
  type: 'rating' | 'detailed';
  value: number | string;
}

export function useFeedbackSystem(agentId: string) {
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats>({ rating: 0 });

  const submitFeedback = async (data: FeedbackData) => {
    // Implement feedback submission logic here
    console.log('Submitting feedback:', data);
  };

  return {
    submitFeedback,
    feedbackStats
  };
} 