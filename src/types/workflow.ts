export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: WorkflowStatus;
  type: WorkflowType;
  config: WorkflowConfig;
}

export enum WorkflowStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum WorkflowType {
  RESEARCH = 'research',
  ANALYSIS = 'analysis',
  DEVELOPMENT = 'development'
}

export interface WorkflowConfig {
  agents: string[];
  maxDuration?: number;
  retryAttempts?: number;
  priority?: 'low' | 'medium' | 'high';
}

export interface WorkflowState {
  workflows: Workflow[];
  activeWorkflow: string | null;
  status: WorkflowStatus;
  progress: number;
} 