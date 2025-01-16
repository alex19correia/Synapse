import React from 'react';
import type { BackupData } from '@/services/BackupService';

interface CreateBackupProps {
    onSubmit: (data: BackupData) => Promise<void>;
}

export const CreateBackup: React.FC<CreateBackupProps> = ({ onSubmit }) => {
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        const data: BackupData = {
            type: form.type.value,
            description: form.description.value
        };
        await onSubmit(data);
        form.reset();
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label htmlFor="type">Backup Type</label>
                <input
                    id="type"
                    name="type"
                    type="text"
                    required
                    className="input"
                />
            </div>
            <div>
                <label htmlFor="description">Description</label>
                <textarea
                    id="description"
                    name="description"
                    className="textarea"
                />
            </div>
            <button type="submit" className="btn btn-primary">
                Create Backup
            </button>
        </form>
    );
}; 