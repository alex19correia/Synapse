import { NextResponse } from 'next/server';
import { BackupService } from '@/services/BackupService';
import { validateRequest } from '@/lib/security';

export async function POST(req: Request) {
    try {
        const validation = await validateRequest(req);
        if (!validation.valid) {
            return NextResponse.json(
                { error: 'Unauthorized' },
                { status: 401 }
            );
        }

        const data = await req.json();
        const backup = await BackupService.createBackup(data);
        
        return NextResponse.json(backup);
    } catch (error) {
        console.error('Backup failed:', error);
        return NextResponse.json(
            { error: 'Backup operation failed' },
            { status: 500 }
        );
    }
}

export async function GET(req: Request) {
    try {
        const validation = await validateRequest(req);
        if (!validation.valid) {
            return NextResponse.json(
                { error: 'Unauthorized' },
                { status: 401 }
            );
        }

        const backups = await BackupService.listBackups();
        return NextResponse.json(backups);
    } catch (error) {
        console.error('Failed to fetch backups:', error);
        return NextResponse.json(
            { error: 'Failed to fetch backups' },
            { status: 500 }
        );
    }
} 