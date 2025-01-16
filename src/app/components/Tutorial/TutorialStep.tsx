'use client';

interface StepProps {
  step: {
    title: string;
    description: string;
  };
  progress: number;
}

export function TutorialStep({ step, progress }: StepProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">{step.title}</h3>
      <p className="text-gray-400">{step.description}</p>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
} 