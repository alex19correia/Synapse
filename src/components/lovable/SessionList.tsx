/** @generated-by-lovable - DO NOT EDIT */
"use client";
import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { Plus, MessageSquare } from 'lucide-react';
import { useSessions } from '../../hooks/useSessions';

export function SessionList() {
  const router = useRouter();
  const { sessions, createSession, deleteSession, isLoading } = useSessions();

  const handleNewSession = async () => {
    const session = await createSession();
    router.push(`/chat/${session.id}`);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <Button 
          onClick={handleNewSession} 
          className="w-full"
          disabled={isLoading}
        >
          <Plus className="mr-2 h-4 w-4" />
          Nova Conversa
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-2">
          {sessions.map((session) => (
            <SessionCard 
              key={session.id}
              session={session}
              onDelete={() => deleteSession(session.id)}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

interface SessionCardProps {
  session: {
    id: string;
    title: string;
    lastMessage?: string;
    createdAt: Date;
  };
  onDelete: () => void;
}

function SessionCard({ session, onDelete }: SessionCardProps) {
  const router = useRouter();

  return (
    <Button
      variant="ghost"
      className="w-full justify-start"
      onClick={() => router.push(`/chat/${session.id}`)}
    >
      <MessageSquare className="mr-2 h-4 w-4" />
      <div className="flex-1 text-left">
        <div className="font-medium">{session.title}</div>
        {session.lastMessage && (
          <div className="text-sm text-muted-foreground truncate">
            {session.lastMessage}
          </div>
        )}
      </div>
    </Button>
  );
}
/** @end-lovable */ 