import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';
import { supabase } from '../../../../lib/supabase';

export async function GET() {
  const { userId } = auth();

  if (!userId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    const { data: sessions, error } = await supabase
      .from('chat_sessions')
      .select()
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;

    return NextResponse.json(sessions);
  } catch (error) {
    console.error('Error fetching sessions:', error);
    return new NextResponse('Internal Error', { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { userId } = auth();
    if (!userId) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const { title } = await req.json();

    const { data: session, error } = await supabase
      .from('chat_sessions')
      .insert({
        title,
        user_id: userId,
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json(session);
  } catch (error) {
    console.error('Error creating session:', error);
    return new NextResponse('Internal Error', { status: 500 });
  }
} 