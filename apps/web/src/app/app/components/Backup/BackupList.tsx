import React from 'react';
import type { Backup } from '@/services/BackupService';

interface BackupListProps {
    backups: Backup[];
    onRestore: (backupId: string) => Promise<void>;
}

export const BackupList: React.FC<BackupListProps> = ({ backups, onRestore }) => {
    return (
        <div className="space-y-4">
            {backups.map((backup) => (
                <div key={backup.id} className="flex justify-between items-center p-4 border rounded">
                    <div>
                        <h3 className="font-medium">{backup.type}</h3>
                        <p className="text-sm text-gray-500">{backup.timestamp}</p>
                    </div>
                    <button
                        onClick={() => onRestore(backup.id)}
                        className="btn btn-primary"
                    >
                        Restore
                    </button>
                </div>
            ))}
        </div>
    );
}; 