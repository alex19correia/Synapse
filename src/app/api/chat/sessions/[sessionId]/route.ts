import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { supabase } from '../../../../../lib/supabase';

export const dynamic = 'force-dynamic';

export async function DELETE(request: NextRequest) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const sessionId = request.nextUrl.pathname.split('/')[4];

    // Verifica se a sessão existe e pertence ao usuário
    const { data: session, error: fetchError } = await supabase
      .from('chat_sessions')
      .select()
      .eq('id', sessionId)
      .eq('user_id', userId)
      .single();

    if (fetchError || !session) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    // Deleta a sessão
    const { error: deleteError } = await supabase
      .from('chat_sessions')
      .delete()
      .eq('id', sessionId);

    if (deleteError) throw deleteError;

    return NextResponse.json(null, { status: 204 });
  } catch (error) {
    console.error('Error deleting session:', error);
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
} 