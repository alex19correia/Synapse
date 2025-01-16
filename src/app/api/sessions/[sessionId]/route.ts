import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { supabase } from '@/lib/supabase';

export async function DELETE(
  req: Request,
  { params }: { params: { sessionId: string } }
) {
  const { userId } = auth();

  if (!userId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    // Primeiro verifica se a sessão existe e pertence ao usuário
    const { data: session, error: fetchError } = await supabase
      .from('chat_sessions')
      .select()
      .eq('id', params.sessionId)
      .eq('user_id', userId)
      .single();

    if (fetchError || !session) {
      return new NextResponse('Session not found', { status: 404 });
    }

    // Deleta a sessão
    const { error: deleteError } = await supabase
      .from('chat_sessions')
      .delete()
      .eq('id', params.sessionId);

    if (deleteError) throw deleteError;

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('Error deleting session:', error);
    return new NextResponse('Internal Error', { status: 500 });
  }
} 