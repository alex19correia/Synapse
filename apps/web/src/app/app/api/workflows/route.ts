import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';

export async function POST(req: NextRequest) {
  try {
    const userId = await verifyAuth(req);
    const { workflow } = await req.json();

    // Process workflow here
    
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }
} 