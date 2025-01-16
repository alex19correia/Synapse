import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { db } from '@/lib/db';

export async function POST(req: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const body = await req.json();
    const { title } = body;

    const session = await db.createChatSession(userId, title);
    return NextResponse.json({ session });
  } catch (error) {
    console.error('Erro ao criar sessão:', error);
    return NextResponse.json(
      { error: 'Erro ao criar sessão de chat' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const sessions = await db.getChatSessions(userId);
    return NextResponse.json({ sessions });
  } catch (error) {
    console.error('Erro ao buscar sessões:', error);
    return NextResponse.json(
      { error: 'Erro ao buscar sessões de chat' },
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get('id');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'ID da sessão não fornecido' },
        { status: 400 }
      );
    }

    await db.deleteChatSession(sessionId);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Erro ao deletar sessão:', error);
    return NextResponse.json(
      { error: 'Erro ao deletar sessão de chat' },
      { status: 500 }
    );
  }
} 