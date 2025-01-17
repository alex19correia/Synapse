'use client';

import { useState } from 'react';
import { useWorkflowState } from '@/app/hooks/useWorkflowState';
import { WorkflowCanvas } from './WorkflowCanvas';
import { WorkflowControls } from './WorkflowControls';
import { AgentSelector } from './AgentSelector';
import { useAnalytics } from '@/app/hooks/useAnalytics';

export function WorkflowManager() {
  const { trackWorkflowStart, trackWorkflowComplete } = useAnalytics();
  const { currentWorkflow, isRunning, progress, setWorkflow, startWorkflow, stopWorkflow } = useWorkflowState();
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  const handleStart = async () => {
    if (selectedAgents.length === 0) return;
    trackWorkflowStart(currentWorkflow || 'default');
    startWorkflow();
    // Implementar lógica de execução
  };

  const handleStop = () => {
    stopWorkflow();
    trackWorkflowComplete(currentWorkflow || 'default', progress);
  };

  return (
    <div className="w-full space-y-4">
      <AgentSelector
        selectedAgents={selectedAgents}
        onSelect={setSelectedAgents}
      />
      <WorkflowCanvas
        agents={selectedAgents}
        isRunning={isRunning}
        progress={progress}
      />
      <WorkflowControls
        isRunning={isRunning}
        onStart={handleStart}
        onStop={handleStop}
      />
    </div>
  );
} 