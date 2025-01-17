import React, { useEffect } from 'react';
import { useBackups } from '@/app/hooks/useBackups';
import { BackupList } from './BackupList';
import { CreateBackup } from './CreateBackup';
import { RestoreBackup } from './RestoreBackup';

export const BackupManager: React.FC = () => {
    const {
        backups,
        loading,
        error,
        createBackup,
        restoreBackup,
        loadBackups
    } = useBackups();

    useEffect(() => {
        loadBackups();
    }, [loadBackups]);

    if (loading) return <div>Loading backups...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div className="space-y-6">
            <CreateBackup
                onSubmit={async (data) => {
                    await createBackup(data);
                }}
            />
            
            <BackupList
                backups={backups}
                onRestore={async (backupId) => {
                    await restoreBackup(backupId);
                }}
            />
            
            <RestoreBackup
                backups={backups}
                onRestore={async (backupId, components) => {
                    await restoreBackup(backupId, { components });
                }}
            />
        </div>
    );
}; 