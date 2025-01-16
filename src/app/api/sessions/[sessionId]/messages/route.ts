import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { supabase } from '../../../../../lib/supabase';
import type { Message, NewMessage } from '../../../../../types/supabase';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const sessionId = request.nextUrl.pathname.split('/')[3];

    // Verifica se a sessão existe e pertence ao usuário
    const { data: session, error: sessionError } = await supabase
      .from('chat_sessions')
      .select()
      .eq('id', sessionId)
      .eq('user_id', userId)
      .single();

    if (sessionError || !session) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    // Busca as mensagens da sessão
    const { data: messages, error: messagesError } = await supabase
      .from('messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true });

    if (messagesError) throw messagesError;

    return NextResponse.json({ messages });
  } catch (error) {
    console.error('Error fetching messages:', error);
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const sessionId = request.nextUrl.pathname.split('/')[3];
    const { content } = await request.json() as { content: string };

    // Verifica se a sessão existe e pertence ao usuário
    const { data: session, error: sessionError } = await supabase
      .from('chat_sessions')
      .select()
      .eq('id', sessionId)
      .eq('user_id', userId)
      .single();

    if (sessionError || !session) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    const userMessageData: NewMessage = {
      content,
      role: 'user',
      session_id: sessionId,
      created_at: new Date().toISOString()
    };

    // Salva a mensagem do usuário
    const { data: userMessage, error: userMessageError } = await supabase
      .from('messages')
      .insert(userMessageData)
      .select()
      .single();

    if (userMessageError) throw userMessageError;

    // Processa a resposta do assistente
    const assistantResponse = await processAssistantResponse(content);

    const assistantMessageData: NewMessage = {
      content: assistantResponse,
      role: 'assistant',
      session_id: sessionId,
      created_at: new Date().toISOString()
    };

    // Salva a resposta do assistente
    const { data: assistantMessage, error: assistantMessageError } = await supabase
      .from('messages')
      .insert(assistantMessageData)
      .select()
      .single();

    if (assistantMessageError) throw assistantMessageError;

    return NextResponse.json({ messages: [userMessage, assistantMessage] });
  } catch (error) {
    console.error('Error processing message:', error);
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}

// Função auxiliar para processar a resposta do assistente
async function processAssistantResponse(userMessage: string): Promise<string> {
  // TODO: Implementar a integração real com o modelo de IA
  return `Resposta simulada para: ${userMessage}`;
} 