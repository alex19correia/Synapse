import { useState } from 'react';

interface OnboardingStep {
  title: string;
  description: string;
}

interface OnboardingState {
  steps: OnboardingStep[];
  currentStep: number;
  completed: boolean;
  totalSteps: number;
  progress: number;
}

export function useOnboarding() {
  const [state, setState] = useState<OnboardingState>({
    steps: [
      { title: 'Welcome', description: 'Get started with the platform' },
      { title: 'Setup', description: 'Configure your preferences' },
      { title: 'Complete', description: 'You\'re all set!' }
    ],
    currentStep: 0,
    completed: false,
    totalSteps: 3,
    progress: 0
  });

  const nextStep = () => {
    setState(prev => ({
      ...prev,
      currentStep: prev.currentStep + 1,
      completed: prev.currentStep === prev.totalSteps - 1,
      progress: ((prev.currentStep + 1) / prev.totalSteps) * 100
    }));
  };

  const previousStep = () => {
    setState(prev => ({
      ...prev,
      currentStep: Math.max(0, prev.currentStep - 1),
      progress: ((prev.currentStep - 1) / prev.totalSteps) * 100
    }));
  };

  return {
    ...state,
    nextStep,
    previousStep
  };
} 