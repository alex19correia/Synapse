import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function GET() {
    const session = await auth();
    
    if (!session.userId) {
        return NextResponse.json({ 
            error: 'Not authenticated',
            message: 'Please sign in first'
        }, { status: 401 });
    }

    return NextResponse.json({
        authenticated: true,
        userId: session.userId
    });
} 