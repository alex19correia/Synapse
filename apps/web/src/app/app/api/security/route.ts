import { NextResponse } from 'next/server';
import { SecurityService } from '@/services/SecurityService';

export async function GET(req: Request) {
    try {
        const userId = req.headers.get('user-id');
        if (!userId) {
            return NextResponse.json({ error: 'User ID required' }, { status: 400 });
        }

        const permissions = await SecurityService.validatePermissions(userId);
        return NextResponse.json(permissions);
    } catch (error) {
        return NextResponse.json({ error: 'Security check failed' }, { status: 500 });
    }
} 