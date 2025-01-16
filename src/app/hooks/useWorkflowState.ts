import { create } from 'zustand';

interface WorkflowState {
    currentWorkflow: string | null;
    isRunning: boolean;
    progress: number;
    setWorkflow: (workflow: string) => void;
    startWorkflow: () => void;
    stopWorkflow: () => void;
    updateProgress: (progress: number) => void;
}

export const useWorkflowState = create<WorkflowState>((set) => ({
    currentWorkflow: null,
    isRunning: false,
    progress: 0,
    setWorkflow: (workflow) => set({ currentWorkflow: workflow }),
    startWorkflow: () => set({ isRunning: true }),
    stopWorkflow: () => set({ isRunning: false, progress: 0 }),
    updateProgress: (progress) => set({ progress })
})); 