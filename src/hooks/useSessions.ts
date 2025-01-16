/** @generated-by-lovable - DO NOT EDIT */
import { useState, useCallback, useEffect } from 'react';
import { useToast } from '@/components/ui/use-toast';

interface Session {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: Date;
}

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // Carrega sessões iniciais
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/chat/sessions');
      if (!response.ok) throw new Error('Falha ao carregar sessões');
      
      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      toast({
        title: 'Erro ao carregar sessões',
        description: 'Tente novamente mais tarde.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const createSession = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch('/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'Nova Conversa' }),
      });

      if (!response.ok) throw new Error('Falha ao criar sessão');
      
      const newSession = await response.json();
      setSessions(prev => [...prev, newSession]);
      return newSession;

    } catch (error) {
      toast({
        title: 'Erro ao criar sessão',
        description: 'Tente novamente mais tarde.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`/api/chat/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Falha ao deletar sessão');

      setSessions(prev => prev.filter(session => session.id !== sessionId));

    } catch (error) {
      toast({
        title: 'Erro ao deletar sessão',
        description: 'Tente novamente mais tarde.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    sessions,
    createSession,
    deleteSession,
    isLoading,
  };
}
/** @end-lovable */ 