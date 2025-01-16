import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { supabase } from '../../../../../lib/supabase';
import { openai } from '../../../../../lib/openai';
import type { NewMessage } from '../../../../../types/supabase';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const sessionId = request.nextUrl.pathname.split('/')[3];

    const { data: messages, error } = await supabase
      .from('messages')
      .select()
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ messages });
  } catch (error) {
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const sessionId = request.nextUrl.pathname.split('/')[3];
    const { content } = await request.json();

    const userMessage = {
      content,
      role: 'user' as const,
      session_id: sessionId,
      created_at: new Date().toISOString()
    } satisfies NewMessage;

    const { data: savedUserMessage, error: userError } = await supabase
      .from('messages')
      .insert(userMessage)
      .select()
      .single();

    if (userError) {
      return NextResponse.json({ error: userError.message }, { status: 500 });
    }

    const assistantResponse = await processAssistantResponse(content);

    const assistantMessage = {
      content: assistantResponse,
      role: 'assistant' as const,
      session_id: sessionId,
      created_at: new Date().toISOString()
    } satisfies NewMessage;

    const { data: savedAssistantMessage, error: assistantError } = await supabase
      .from('messages')
      .insert(assistantMessage)
      .select()
      .single();

    if (assistantError) {
      return NextResponse.json({ error: assistantError.message }, { status: 500 });
    }

    return NextResponse.json({
      messages: [savedUserMessage, savedAssistantMessage]
    });
  } catch (error) {
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}

async function processAssistantResponse(userMessage: string): Promise<string> {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "Você é um assistente útil e amigável que ajuda os usuários com suas dúvidas e tarefas."
        },
        {
          role: "user",
          content: userMessage
        }
      ],
      temperature: 0.7,
      max_tokens: 500,
    });

    return completion.choices[0].message.content || "Desculpe, não consegui processar sua mensagem.";
  } catch (error) {
    console.error('Error processing assistant response:', error);
    return "Desculpe, ocorreu um erro ao processar sua mensagem.";
  }
} 