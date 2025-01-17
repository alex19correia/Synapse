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

export async function GET(
    req: Request,
    { params }: { params: { sessionId: string } }
) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { searchParams } = new URL(req.url);
        const limit = parseInt(searchParams.get('limit') || '50');
        const beforeId = searchParams.get('before_id') || undefined;
        const statusParam = searchParams.get('status');
        const status = statusParam as 'sent' | 'delivered' | 'error' | undefined;
        
        const messages = await chatService.getSessionMessages(
            params.sessionId,
            limit,
            beforeId,
            status
        );
        
        return NextResponse.json(messages);
    } catch (error) {
        console.error('Error fetching messages:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
}

export async function POST(
    req: Request,
    { params }: { params: { sessionId: string } }
) {
    const { userId } = auth();
    if (!userId) {
        return new NextResponse('Unauthorized', { status: 401 });
    }

    try {
        const { content, role = 'user', metadata } = await req.json();
        
        if (!content) {
            return new NextResponse('Content is required', { status: 400 });
        }
        
        const message = await chatService.addMessage(
            params.sessionId,
            content,
            role as 'user' | 'assistant' | 'system',
            metadata
        );
        
        return NextResponse.json(message);
    } catch (error) {
        console.error('Error adding message:', error);
        return new NextResponse('Internal Error', { status: 500 });
    }
} 