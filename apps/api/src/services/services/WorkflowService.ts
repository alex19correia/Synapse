import { api } from '@/lib/api';

export interface Workflow {
    id: string;
    name: string;
    status: string;
    steps: WorkflowStep[];
}

export interface WorkflowStep {
    id: string;
    type: string;
    config: any;
}

export class WorkflowService {
    static async getWorkflows(): Promise<Workflow[]> {
        const response = await api.get('/api/workflows');
        return response.data;
    }

    static async createWorkflow(data: Partial<Workflow>): Promise<Workflow> {
        const response = await api.post('/api/workflows', data);
        return response.data;
    }

    static async updateWorkflow(id: string, data: Partial<Workflow>): Promise<Workflow> {
        const response = await api.put(`/api/workflows/${id}`, data);
        return response.data;
    }

    static async deleteWorkflow(id: string): Promise<void> {
        await api.delete(`/api/workflows/${id}`);
    }
} 