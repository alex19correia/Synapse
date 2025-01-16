import { useState, useEffect } from 'react';

interface TutorialStep {
  title: string;
  description: string;
  startingCode: string;
  solution: string;
}

interface Tutorial {
  id: string;
  title: string;
  steps: TutorialStep[];
}

export function useTutorial(tutorialId: string) {
  const [currentStep, setCurrentStep] = useState(0);
  const [tutorial, setTutorial] = useState<Tutorial | null>(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);

  const checkSolution = async (code: string) => {
    // Implement solution checking logic
    return code === tutorial?.steps[currentStep].solution;
  };

  useEffect(() => {
    // Simulate loading tutorial data
    setTutorial({
      id: tutorialId,
      title: 'Sample Tutorial',
      steps: [
        {
          title: 'First Step',
          description: 'Getting started',
          startingCode: 'console.log("Hello")',
          solution: 'console.log("Hello, World!")'
        }
      ]
    });
    setLoading(false);
  }, [tutorialId]);

  return {
    currentStep,
    tutorial,
    checkSolution,
    progress,
    loading
  };
} 