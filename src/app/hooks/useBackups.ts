import { create } from 'zustand';
import { BackupService, Backup, BackupData } from '@/services/BackupService';

interface BackupState {
    backups: Backup[];
    loading: boolean;
    error: Error | null;
    createBackup: (data: BackupData) => Promise<void>;
    restoreBackup: (backupId: string, options?: { components?: string[] }) => Promise<void>;
    loadBackups: () => Promise<void>;
}

export const useBackups = create<BackupState>((set) => ({
    backups: [],
    loading: false,
    error: null,
    createBackup: async (data) => {
        set({ loading: true });
        try {
            const newBackup = await BackupService.createBackup(data);
            set((state) => ({
                backups: [...state.backups, newBackup],
                loading: false
            }));
        } catch (err) {
            set({ error: err as Error, loading: false });
        }
    },
    restoreBackup: async (backupId, options) => {
        set({ loading: true });
        try {
            await BackupService.restoreBackup(backupId, options?.components);
            set({ loading: false });
        } catch (err) {
            set({ error: err as Error, loading: false });
        }
    },
    loadBackups: async () => {
        set({ loading: true });
        try {
            const backups = await BackupService.listBackups();
            set({ backups, loading: false });
        } catch (err) {
            set({ error: err as Error, loading: false });
        }
    }
})); 