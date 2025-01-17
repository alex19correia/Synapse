import React from 'react';
import type { Backup } from '@/services/BackupService';

interface RestoreBackupProps {
    backups: Backup[];
    onRestore: (backupId: string, components?: string[]) => Promise<void>;
}

export const RestoreBackup: React.FC<RestoreBackupProps> = ({ backups, onRestore }) => {
    const [selectedComponents, setSelectedComponents] = React.useState<string[]>([]);

    return (
        <div className="space-y-4">
            <h2>Restore Backup</h2>
            <select
                onChange={(e) => {
                    if (e.target.value) {
                        onRestore(e.target.value, selectedComponents);
                    }
                }}
                className="select"
            >
                <option value="">Select a backup</option>
                {backups.map((backup) => (
                    <option key={backup.id} value={backup.id}>
                        {backup.type} - {backup.timestamp}
                    </option>
                ))}
            </select>
        </div>
    );
}; 