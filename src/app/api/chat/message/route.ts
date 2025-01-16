import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { db } from '@/lib/db';
import { OpenAIProvider } from '@/lib/llm/providers';

const llm = new OpenAIProvider(process.env.OPENAI_API_KEY!);

export async function POST(req: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const body = await req.json();
    const { sessionId, message } = body;

    if (!sessionId || !message) {
      return NextResponse.json(
        { error: 'Sessão e mensagem são obrigatórios' },
        { status: 400 }
      );
    }

    // Verifica se a sessão existe e pertence ao usuário
    const session = await db.getChatSession(sessionId);
    if (!session || session.user_id !== userId) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 });
    }

    // Adiciona a mensagem do usuário
    await db.addMessage(sessionId, 'user', message);

    // Obtém o histórico de mensagens para contexto
    const messages = await db.getMessages(sessionId);
    const messageHistory = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    // Gera resposta do assistente
    const response = await llm.generateResponse(messageHistory);

    // Salva a resposta do assistente
    const assistantMessage = await db.addMessage(sessionId, 'assistant', response.content);

    return NextResponse.json({ message: assistantMessage });
  } catch (error) {
    console.error('Erro ao processar mensagem:', error);
    return NextResponse.json(
      { error: 'Erro ao processar mensagem' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get('sessionId');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'ID da sessão não fornecido' },
        { status: 400 }
      );
    }

    // Verifica se a sessão existe e pertence ao usuário
    const session = await db.getChatSession(sessionId);
    if (!session || session.user_id !== userId) {
      return NextResponse.json({ error: 'Sessão não encontrada' }, { status: 404 });
    }

    const messages = await db.getMessages(sessionId);
    return NextResponse.json({ messages });
  } catch (error) {
    console.error('Erro ao buscar mensagens:', error);
    return NextResponse.json(
      { error: 'Erro ao buscar mensagens' },
      { status: 500 }
    );
  }
} 