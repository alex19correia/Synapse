import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { ChatService } from '@/services/chat_service';
import { env } from '@/env';

// Initialize chat service as a singleton
const chatService = new ChatService(
    env.SUPABASE_URL,
    env.SUPABASE_KEY,
    60  // Persist every 60 seconds
);

export async function GET(req: Request) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { searchParams } = new URL(req.url);
        const statusParam = searchParams.get('status');
        const status = statusParam === 'archived' ? 'archived' : 'active';
        
        const sessions = await chatService.getSessions(userId, status);
        return NextResponse.json(sessions);
    } catch (error) {
        console.error('Error fetching sessions:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
}

export async function POST(req: Request) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { title, metadata } = await req.json();
        
        const session = await chatService.createSession(
            userId,
            title || 'Nova Conversa',
            metadata
        );
        
        return NextResponse.json(session);
    } catch (error) {
        console.error('Error creating session:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
}

// Ensure data is persisted when the server shuts down
process.on('SIGTERM', async () => {
    await chatService.flush();
});

process.on('SIGINT', async () => {
    await chatService.flush();
}); 