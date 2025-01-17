import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { ChatService } from '@/services/chat_service';
import { env } from '@/env';

// Use the same singleton instance
const chatService = new ChatService(
    env.SUPABASE_URL,
    env.SUPABASE_KEY,
    60
);

export async function PATCH(
    req: Request,
    { params }: { params: { sessionId: string } }
) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { status, metadata } = await req.json();
        
        if (!status || !['active', 'archived'].includes(status)) {
            return new NextResponse('Invalid status', { status: 400 });
        }
        
        const session = await chatService.updateSessionStatus(
            params.sessionId,
            status as 'active' | 'archived',
            metadata
        );
        
        return NextResponse.json(session);
    } catch (error) {
        console.error('Error updating session:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
}

export async function DELETE(
    req: Request,
    { params }: { params: { sessionId: string } }
) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { searchParams } = new URL(req.url);
        const hardDelete = searchParams.get('hard') === 'true';
        
        if (hardDelete) {
            const success = await chatService.deleteSession(params.sessionId);
            if (!success) {
                return new NextResponse('Session not found', { status: 404 });
            }
        } else {
            await chatService.archiveSession(params.sessionId);
        }
        
        return new NextResponse(null, { status: 204 });
    } catch (error) {
        console.error('Error deleting session:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
} 