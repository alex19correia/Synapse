/** @generated-by-lovable - DO NOT EDIT */
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Session {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: Date;
}
/** @end-lovable */ 