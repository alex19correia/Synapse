declare module '@/types' {
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