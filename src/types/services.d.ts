declare module '@/services/*' {
    // WorkflowService types
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

    // SecurityService types
    export interface SecurityConfig {
        token?: string;
        permissions?: string[];
    }

    // BackupService types (já definido, mas incluído aqui para completude)
    export interface BackupData {
        type: string;
        description?: string;
    }

    export interface Backup {
        id: string;
        type: string;
        timestamp: string;
        status: string;
        description?: string;
    }
} 