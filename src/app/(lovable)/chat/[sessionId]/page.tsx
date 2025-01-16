/** @generated-by-lovable - DO NOT EDIT */
'use client';

import { useParams } from 'next/navigation';
import { ChatWindow } from '@/components/lovable/ChatWindow';

interface PageProps {
  params?: {
    sessionId?: string;
  };
}

export default function ChatPage() {
  const params = useParams();
  const sessionId = params?.sessionId as string;

  if (!sessionId) {
    return <div>Sessão não encontrada</div>;
  }

  return (
    <div className="flex flex-col h-screen">
      <ChatWindow sessionId={sessionId} />
    </div>
  );
}
/** @end-lovable */ 