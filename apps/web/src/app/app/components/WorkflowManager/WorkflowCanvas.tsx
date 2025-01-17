'use client';

interface WorkflowCanvasProps {
  agents: string[];
  isRunning: boolean;
  progress: number;
}

export function WorkflowCanvas({ agents, isRunning, progress }: WorkflowCanvasProps) {
  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-800/50">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">Workflow Canvas</h3>
          <span className="text-sm text-gray-400">
            {isRunning ? `Progress: ${progress}%` : 'Ready'}
          </span>
        </div>
        
        <div className="grid grid-cols-1 gap-4">
          {agents.map((agent, index) => (
            <div
              key={agent}
              className="p-3 bg-gray-700/50 rounded-md flex items-center justify-between"
            >
              <span>{agent}</span>
              {isRunning && (
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 