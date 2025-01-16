/** @generated-by-lovable - DO NOT EDIT */
"use client";
import { useState, useCallback, useEffect } from 'react';
import { Message } from '@/types/chat';
import { useToast } from '@/components/ui/use-toast';

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // Load initial messages
  useEffect(() => {
    if (sessionId) {
      loadMessages();
    }
  }, [sessionId]);

  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/chat/${sessionId}/messages`);
      if (!response.ok) throw new Error('Failed to load messages');
      
      const data = await response.json();
      setMessages(data.messages);
    } catch (error) {
      toast({
        title: 'Error loading messages',
        description: 'Please try again later.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = useCallback(async (content: string) => {
    try {
      setIsLoading(true);
      
      // Add user message
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Get previous messages in the format DeepSeek expects
      const messageHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Send to DeepSeek API
      const response = await fetch(`/api/test/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messageHistory, { role: 'user', content }],
          model: 'deepseek-chat',
          use_rag: false
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      
      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      toast({
        title: 'Error sending message',
        description: 'Please try again later.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [messages, toast]);

  return {
    messages,
    sendMessage,
    isLoading,
  };
}
/** @end-lovable */ 