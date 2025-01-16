/** @generated-by-lovable - DO NOT EDIT */
import React from 'react';
import { useChat } from '../../hooks/useChat';
import { Message } from '../../types/chat';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar } from '../ui/avatar';
import { Loader2 } from 'lucide-react';

interface ChatWindowProps {
  sessionId: string;
}

export function ChatWindow({ sessionId }: ChatWindowProps) {
  const { messages, sendMessage, isLoading } = useChat(sessionId);
  const [input, setInput] = React.useState('');
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    await sendMessage(input);
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea ref={scrollRef} className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <MessageCard key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-center">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            disabled={isLoading}
          />
          <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
            Enviar
          </Button>
        </div>
      </div>
    </div>
  );
}

interface MessageCardProps {
  message: Message;
}

function MessageCard({ message }: MessageCardProps) {
  const isUser = message.role === 'user';

  return (
    <Card className={`flex gap-3 p-4 ${isUser ? 'bg-primary/10' : 'bg-muted'}`}>
      <Avatar>
        <div className={`h-10 w-10 rounded-full ${isUser ? 'bg-primary' : 'bg-secondary'}`}>
          {isUser ? 'U' : 'A'}
        </div>
      </Avatar>
      <div className="flex-1">
        <div className="font-semibold">
          {isUser ? 'Você' : 'Assistente'}
        </div>
        <div className="mt-1 text-sm">
          {message.content}
        </div>
      </div>
    </Card>
  );
}
/** @end-lovable */ 