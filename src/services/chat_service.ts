import { SupabaseClient, createClient } from '@supabase/supabase-js';

// Types
export interface Session {
    id: string;
    user_id: string;
    title: string;
    status: 'active' | 'archived';
    metadata: Record<string, any>;
    last_message_at: string;
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: string;
    session_id: string;
    content: string;
    role: 'user' | 'assistant' | 'system';
    status: 'sent' | 'delivered' | 'error';
    metadata: Record<string, any>;
    created_at: string;
}

export class ChatService {
    private supabase: SupabaseClient;
    private sessionsCache: Map<string, Map<string, Session>>;
    private messagesCache: Map<string, Message[]>;
    private dirtySessions: Set<string>;
    private dirtyMessages: Set<string>;
    private persistInterval: number;
    private persistTimer: ReturnType<typeof setInterval> | null;

    constructor(supabaseUrl: string, supabaseKey: string, persistInterval: number = 60) {
        this.supabase = createClient(supabaseUrl, supabaseKey);
        this.sessionsCache = new Map();
        this.messagesCache = new Map();
        this.dirtySessions = new Set();
        this.dirtyMessages = new Set();
        this.persistInterval = persistInterval * 1000;
        this.persistTimer = null;
        
        this.startPersistenceWorker();
        console.debug("🔧 ChatService initialized with in-memory cache and Supabase persistence");
    }

    private startPersistenceWorker(): void {
        this.persistTimer = setInterval(async () => {
            try {
                await this.persistDirtyData();
            } catch (error) {
                console.error("❌ Error in persistence worker:", error);
            }
        }, this.persistInterval);
    }

    private async persistDirtyData(): Promise<void> {
        try {
            // Persist dirty sessions
            if (this.dirtySessions.size > 0) {
                const sessionsToPersist: Session[] = [];
                this.sessionsCache.forEach(userSessions => {
                    userSessions.forEach(session => {
                        if (this.dirtySessions.has(session.id)) {
                            sessionsToPersist.push(session);
                        }
                    });
                });

                if (sessionsToPersist.length > 0) {
                    await this.supabase
                        .from('chat_sessions')
                        .upsert(sessionsToPersist);
                }

                this.dirtySessions.clear();
                console.debug(`💾 Persisted ${sessionsToPersist.length} sessions to Supabase`);
            }

            // Persist dirty messages
            if (this.dirtyMessages.size > 0) {
                const messagesToPersist: Message[] = [];
                this.dirtyMessages.forEach(sessionId => {
                    const messages = this.messagesCache.get(sessionId);
                    if (messages) {
                        messagesToPersist.push(...messages);
                    }
                });

                if (messagesToPersist.length > 0) {
                    await this.supabase
                        .from('messages')
                        .upsert(messagesToPersist);
                }

                this.dirtyMessages.clear();
                console.debug(`💾 Persisted ${messagesToPersist.length} messages to Supabase`);
            }
        } catch (error) {
            console.error("❌ Error persisting data:", error);
            // Keep items marked as dirty if persistence fails
        }
    }

    async createSession(
        userId: string,
        title: string = "Nova Conversa",
        metadata: Record<string, any> = {}
    ): Promise<Session> {
        const now = new Date().toISOString();
        const session: Session = {
            id: crypto.randomUUID(),
            user_id: userId,
            title,
            status: 'active',
            metadata,
            last_message_at: now,
            created_at: now,
            updated_at: now
        };

        // Add to cache
        if (!this.sessionsCache.has(userId)) {
            this.sessionsCache.set(userId, new Map());
        }
        this.sessionsCache.get(userId)!.set(session.id, session);
        this.dirtySessions.add(session.id);

        console.debug(`✅ Created chat session for user ${userId} in cache`);
        return session;
    }

    async getSessions(userId: string, status?: 'active' | 'archived'): Promise<Session[]> {
        // Check cache first
        if (this.sessionsCache.has(userId)) {
            const sessions = Array.from(this.sessionsCache.get(userId)!.values())
                .filter(session => !status || session.status === status)
                .sort((a, b) => b.last_message_at.localeCompare(a.last_message_at));
            return sessions;
        }

        // If not in cache, get from Supabase and cache
        const query = this.supabase
            .from('chat_sessions')
            .select('*')
            .eq('user_id', userId);

        if (status) {
            query.eq('status', status);
        }

        const { data: sessions, error } = await query
            .order('last_message_at', { ascending: false });

        if (error) throw error;

        // Cache the results
        const userSessions = new Map();
        sessions.forEach(session => userSessions.set(session.id, session));
        this.sessionsCache.set(userId, userSessions);

        console.debug(`📚 Retrieved ${sessions.length} sessions for user ${userId}`);
        return sessions;
    }

    async addMessage(
        sessionId: string,
        content: string,
        role: 'user' | 'assistant' | 'system' = 'user',
        metadata: Record<string, any> = {},
        status: 'sent' | 'delivered' | 'error' = 'sent'
    ): Promise<Message> {
        if (!sessionId || !content) {
            throw new Error("Session ID and content are required");
        }

        const message: Message = {
            id: crypto.randomUUID(),
            session_id: sessionId,
            content,
            role,
            status,
            metadata,
            created_at: new Date().toISOString()
        };

        // Add to cache
        if (!this.messagesCache.has(sessionId)) {
            this.messagesCache.set(sessionId, []);
        }
        this.messagesCache.get(sessionId)!.push(message);
        this.dirtyMessages.add(sessionId);

        // Update session's last_message_at in cache
        this.sessionsCache.forEach(userSessions => {
            const session = userSessions.get(sessionId);
            if (session) {
                session.last_message_at = message.created_at;
                session.updated_at = message.created_at;
                this.dirtySessions.add(sessionId);
            }
        });

        console.debug(`💬 Added ${role} message to session ${sessionId} in cache`);
        return message;
    }

    async getSessionMessages(
        sessionId: string,
        limit: number = 50,
        beforeId?: string,
        status?: 'sent' | 'delivered' | 'error'
    ): Promise<Message[]> {
        // Check cache first
        if (this.messagesCache.has(sessionId)) {
            let messages = this.messagesCache.get(sessionId)!;

            if (status) {
                messages = messages.filter(m => m.status === status);
            }
            if (beforeId) {
                messages = messages.filter(m => m.id < beforeId);
            }

            messages.sort((a, b) => b.created_at.localeCompare(a.created_at));
            return messages.slice(0, limit);
        }

        // If not in cache, get from Supabase and cache
        const query = this.supabase
            .from('messages')
            .select('*')
            .eq('session_id', sessionId);

        if (status) {
            query.eq('status', status);
        }
        if (beforeId) {
            query.lt('id', beforeId);
        }

        const { data: messages, error } = await query
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) throw error;

        // Cache the results
        this.messagesCache.set(sessionId, messages);

        console.debug(`📜 Retrieved ${messages.length} messages from session ${sessionId}`);
        return messages;
    }

    async updateSessionStatus(
        sessionId: string,
        status: 'active' | 'archived',
        metadata?: Record<string, any>
    ): Promise<Session> {
        // Update in cache if present
        let foundSession: Session | undefined;
        this.sessionsCache.forEach(userSessions => {
            const cachedSession = userSessions.get(sessionId);
            if (cachedSession) {
                cachedSession.status = status;
                cachedSession.updated_at = new Date().toISOString();
                if (metadata) {
                    cachedSession.metadata = metadata;
                }
                this.dirtySessions.add(sessionId);
                foundSession = cachedSession;
            }
        });

        // If not in cache, update directly in Supabase
        if (!foundSession) {
            const updateData: Partial<Session> = {
                status,
                updated_at: new Date().toISOString()
            };
            if (metadata) {
                updateData.metadata = metadata;
            }

            const { data, error } = await this.supabase
                .from('chat_sessions')
                .update(updateData)
                .eq('id', sessionId)
                .select()
                .single();

            if (error) throw error;
            if (!data) throw new Error('Session not found');
            foundSession = data;
        }

        if (!foundSession) {
            throw new Error('Failed to update session status');
        }

        console.debug(`📝 Updated session ${sessionId} status to ${status}`);
        return foundSession;
    }

    async archiveSession(sessionId: string): Promise<Session> {
        return this.updateSessionStatus(sessionId, 'archived');
    }

    async deleteSession(sessionId: string): Promise<boolean> {
        try {
            // Remove from cache
            this.sessionsCache.forEach(userSessions => {
                userSessions.delete(sessionId);
            });
            this.messagesCache.delete(sessionId);

            // Remove from Supabase
            await this.supabase
                .from('messages')
                .delete()
                .eq('session_id', sessionId);

            const { error, count } = await this.supabase
                .from('chat_sessions')
                .delete()
                .eq('id', sessionId)
                .select('count');

            if (error) throw error;

            const success = (count ?? 0) > 0;
            if (success) {
                console.debug(`🗑️ Deleted session ${sessionId} and its messages`);
            }
            return success;
        } catch (error) {
            console.error("❌ Error deleting session:", error);
            throw error;
        }
    }

    async flush(): Promise<void> {
        await this.persistDirtyData();
    }

    destroy(): void {
        if (this.persistTimer) {
            clearInterval(this.persistTimer);
            this.persistTimer = null;
        }
    }
} 