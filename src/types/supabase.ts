export interface ChatSession {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  last_message?: string;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  session_id: string;
  created_at: string;
}

export type NewChatSession = Omit<ChatSession, 'id' | 'last_message'>;
export type NewMessage = Omit<Message, 'id'>;

export interface Database {
  public: {
    Tables: {
      chat_sessions: {
        Row: ChatSession;
        Insert: NewChatSession;
        Update: Partial<ChatSession>;
      };
      messages: {
        Row: Message;
        Insert: NewMessage;
        Update: Partial<Message>;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
} 