'use client';

interface WorkflowControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onStop: () => void;
}

export function WorkflowControls({ isRunning, onStart, onStop }: WorkflowControlsProps) {
  return (
    <div className="flex justify-end space-x-4">
      {!isRunning ? (
        <button
          onClick={onStart}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-md text-white font-medium transition-colors"
        >
          Start Workflow
        </button>
      ) : (
        <button
          onClick={onStop}
          className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-md text-white font-medium transition-colors"
        >
          Stop Workflow
        </button>
      )}
    </div>
  );
} 