import { clerkClient } from '@clerk/nextjs/server';
import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function GET() {
    const { userId } = await auth();
    
    if (!userId) {
        return NextResponse.json({ 
            error: 'No active session',
            message: 'Please sign in first'
        }, { status: 401 });
    }

    try {
        const client = await clerkClient();
        const token = await client.sessions.getToken(userId, {
            template: "Synapsetest"
        });

        return NextResponse.json({ 
            userId,
            token,
            message: 'You can use this token for testing'
        });
    } catch (error) {
        console.error('Error generating token:', error);
        return NextResponse.json({ 
            error: 'Failed to generate token',
            message: 'Please try again'
        }, { status: 500 });
    }
} 