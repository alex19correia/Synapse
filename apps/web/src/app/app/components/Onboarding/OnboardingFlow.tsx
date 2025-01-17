'use client';

import { useOnboarding } from '@/app/hooks/useOnboarding';

interface ProgressProps {
  value: number;
  total: number;
  label?: string;
}

interface StepProps {
  title: string;
  description: string;
  onComplete: (data: any) => Promise<void>;
}

function Progress({ value, total, label }: ProgressProps) {
  const percentage = (value / total) * 100;
  return (
    <div className="w-full bg-gray-700 rounded-full h-2">
      <div
        className="bg-blue-500 h-2 rounded-full transition-all"
        style={{ width: `${percentage}%` }}
      />
      {label && <span className="text-sm text-gray-400 mt-1">{label}</span>}
    </div>
  );
}

function Step({ title, description, onComplete }: StepProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-gray-400">{description}</p>
      <button
        onClick={() => onComplete({})}
        className="px-4 py-2 bg-blue-500 rounded-md"
      >
        Complete
      </button>
    </div>
  );
}

export function OnboardingFlow() {
  const {
    steps,
    currentStep,
    completed,
    totalSteps,
    progress,
    nextStep,
    previousStep
  } = useOnboarding();

  if (completed) {
    return <div>Onboarding completed! 🎉</div>;
  }

  return (
    <div className="space-y-8">
      <Progress
        value={currentStep + 1}
        total={totalSteps}
        label={`Step ${currentStep + 1} of ${totalSteps}`}
      />
      
      <Step
        title={steps[currentStep].title}
        description={steps[currentStep].description}
        onComplete={async () => {
          nextStep();
        }}
      />

      <div className="flex justify-between">
        {currentStep > 0 && (
          <button
            onClick={previousStep}
            className="px-4 py-2 bg-gray-700 rounded-md"
          >
            Previous
          </button>
        )}
      </div>
    </div>
  );
} 