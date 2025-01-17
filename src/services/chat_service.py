from typing import Optional, List, Dict, Any
from loguru import logger
from fastapi import HTTPException
from supabase import create_client, Client
from datetime import datetime
import json
from collections import defaultdict
import asyncio
import threading
from queue import Queue
import uuid

class ChatService:
    """Service to manage chat sessions and messages with in-memory caching."""
    
    def __init__(self, supabase_url: str, supabase_key: str, persist_interval: int = 60):
        """
        Initialize chat service with both Supabase and in-memory cache.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            persist_interval: Interval in seconds to persist cache to Supabase
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # In-memory cache
        self._sessions_cache: Dict[str, Dict] = {}  # user_id -> {session_id -> session}
        self._messages_cache: Dict[str, List[Dict]] = {}  # session_id -> [messages]
        self._dirty_sessions = set()  # Sessions that need to be persisted
        self._dirty_messages = set()  # Messages that need to be persisted
        
        # Persistence queue
        self._persist_queue: Queue = Queue()
        self._persist_interval = persist_interval
        
        # Start persistence thread
        self._start_persistence_worker()
        
        logger.debug("🔧 ChatService initialized with in-memory cache and Supabase persistence")
    
    def _start_persistence_worker(self):
        """Start the background thread for persistence."""
        def persist_worker():
            while True:
                try:
                    # Persist dirty data every interval
                    self._persist_dirty_data()
                    asyncio.run(asyncio.sleep(self._persist_interval))
                except Exception as e:
                    logger.error(f"❌ Error in persistence worker: {str(e)}")
                    
        thread = threading.Thread(target=persist_worker, daemon=True)
        thread.start()
    
    async def _persist_dirty_data(self):
        """Persist dirty sessions and messages to Supabase."""
        try:
            # Persist dirty sessions
            if self._dirty_sessions:
                sessions_to_persist = [
                    self._sessions_cache[user_id][session_id]
                    for session_id in self._dirty_sessions
                    for user_id in self._sessions_cache
                    if session_id in self._sessions_cache[user_id]
                ]
                
                if sessions_to_persist:
                    self.supabase.table("chat_sessions")\
                        .upsert(sessions_to_persist)\
                        .execute()
                    
                self._dirty_sessions.clear()
                logger.debug(f"💾 Persisted {len(sessions_to_persist)} sessions to Supabase")
            
            # Persist dirty messages
            if self._dirty_messages:
                messages_to_persist = [
                    msg for session_id in self._dirty_messages
                    for msg in self._messages_cache.get(session_id, [])
                ]
                
                if messages_to_persist:
                    self.supabase.table("messages")\
                        .upsert(messages_to_persist)\
                        .execute()
                    
                self._dirty_messages.clear()
                logger.debug(f"💾 Persisted {len(messages_to_persist)} messages to Supabase")
                
        except Exception as e:
            logger.error(f"❌ Error persisting data: {str(e)}")
            # Keep items marked as dirty if persistence fails
    
    async def create_session(
        self,
        user_id: str,
        title: str = "Nova Conversa",
        metadata: Dict[str, Any] = None
    ) -> Dict:
        """Create a new chat session in cache and queue for persistence."""
        try:
            session = {
                "id": str(uuid.uuid4()),  # Generate UUID for new session
                "user_id": user_id,
                "title": title,
                "status": "active",
                "metadata": metadata or {},
                "last_message_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add to cache
            if user_id not in self._sessions_cache:
                self._sessions_cache[user_id] = {}
            self._sessions_cache[user_id][session["id"]] = session
            self._dirty_sessions.add(session["id"])
            
            logger.debug(f"✅ Created chat session for user {user_id} in cache")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create chat session")
    
    async def get_sessions(self, user_id: str, status: str = "active") -> List[Dict]:
        """Get chat sessions from cache, falling back to Supabase."""
        try:
            # Check cache first
            if user_id in self._sessions_cache:
                sessions = [
                    session for session in self._sessions_cache[user_id].values()
                    if not status or session["status"] == status
                ]
                sessions.sort(key=lambda x: x["last_message_at"], reverse=True)
                return sessions
            
            # If not in cache, get from Supabase and cache
            query = self.supabase.table("chat_sessions")\
                .select("*")\
                .eq("user_id", user_id)
                
            if status:
                query = query.eq("status", status)
                
            result = query.order("last_message_at", desc=True).execute()
            
            # Cache the results
            self._sessions_cache[user_id] = {
                session["id"]: session for session in result.data
            }
            
            logger.debug(f"📚 Retrieved {len(result.data)} sessions for user {user_id}")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error fetching sessions: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch chat sessions")
    
    async def add_message(
        self,
        session_id: str,
        content: str,
        role: str = "user",
        metadata: Dict[str, Any] = None,
        status: str = "sent"
    ) -> Dict:
        """Add a message to cache and queue for persistence."""
        try:
            # Validate inputs
            if not session_id or not content:
                raise ValueError("Session ID and content are required")
            
            message = {
                "id": str(uuid.uuid4()),  # Generate UUID for new message
                "session_id": session_id,
                "content": content,
                "role": role,
                "status": status,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Add to cache
            if session_id not in self._messages_cache:
                self._messages_cache[session_id] = []
            self._messages_cache[session_id].append(message)
            self._dirty_messages.add(session_id)
            
            # Update session's last_message_at in cache
            for user_sessions in self._sessions_cache.values():
                if session_id in user_sessions:
                    user_sessions[session_id]["last_message_at"] = message["created_at"]
                    user_sessions[session_id]["updated_at"] = message["created_at"]
                    self._dirty_sessions.add(session_id)
                    break
            
            logger.debug(f"💬 Added {role} message to session {session_id} in cache")
            return message
            
        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"❌ Error adding message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to add message")
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 50,
        before_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get messages from cache, falling back to Supabase."""
        try:
            # Check cache first
            if session_id in self._messages_cache:
                messages = self._messages_cache[session_id]
                
                # Apply filters
                if status:
                    messages = [m for m in messages if m["status"] == status]
                if before_id:
                    messages = [m for m in messages if m["id"] < before_id]
                
                # Sort and limit
                messages.sort(key=lambda x: x["created_at"], reverse=True)
                return messages[:limit]
            
            # If not in cache, get from Supabase and cache
            query = self.supabase.table("messages")\
                .select("*")\
                .eq("session_id", session_id)
            
            if status:
                query = query.eq("status", status)
                
            if before_id:
                query = query.lt("id", before_id)
                
            result = query.order("created_at", desc=True).limit(limit).execute()
            
            # Cache the results
            self._messages_cache[session_id] = result.data
            
            logger.debug(f"📜 Retrieved {len(result.data)} messages from session {session_id}")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error fetching messages: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch messages")
    
    async def update_session_status(
        self,
        session_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Update session status in cache and queue for persistence."""
        try:
            # Update in cache if present
            session = None
            for user_sessions in self._sessions_cache.values():
                if session_id in user_sessions:
                    session = user_sessions[session_id]
                    session["status"] = status
                    session["updated_at"] = datetime.utcnow().isoformat()
                    if metadata:
                        session["metadata"] = metadata
                    self._dirty_sessions.add(session_id)
                    break
            
            # If not in cache, update directly in Supabase
            if not session:
                update_data = {
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
                if metadata:
                    update_data["metadata"] = metadata
                    
                result = self.supabase.table("chat_sessions")\
                    .update(update_data)\
                    .eq("id", session_id)\
                    .execute()
                session = result.data[0]
            
            logger.debug(f"📝 Updated session {session_id} status to {status}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error updating session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update session")
    
    async def update_message_status(
        self,
        message_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Update message status in cache and queue for persistence."""
        try:
            # Update in cache if present
            message = None
            for session_messages in self._messages_cache.values():
                for msg in session_messages:
                    if msg["id"] == message_id:
                        msg["status"] = status
                        if metadata:
                            msg["metadata"] = metadata
                        self._dirty_messages.add(msg["session_id"])
                        message = msg
                        break
                if message:
                    break
            
            # If not in cache, update directly in Supabase
            if not message:
                update_data = {"status": status}
                if metadata:
                    update_data["metadata"] = metadata
                    
                result = self.supabase.table("messages")\
                    .update(update_data)\
                    .eq("id", message_id)\
                    .execute()
                message = result.data[0]
            
            logger.debug(f"📝 Updated message {message_id} status to {status}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Error updating message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update message")
    
    async def archive_session(self, session_id: str) -> Dict:
        """Archive a chat session (soft delete)."""
        return await self.update_session_status(session_id, "archived")
    
    async def delete_session(self, session_id: str) -> bool:
        """Hard delete a session from both cache and Supabase."""
        try:
            # Remove from cache
            for user_sessions in self._sessions_cache.values():
                if session_id in user_sessions:
                    del user_sessions[session_id]
            
            if session_id in self._messages_cache:
                del self._messages_cache[session_id]
            
            # Remove from Supabase
            self.supabase.table("messages")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
                
            result = self.supabase.table("chat_sessions")\
                .delete()\
                .eq("id", session_id)\
                .execute()
                
            success = len(result.data) > 0
            if success:
                logger.debug(f"🗑️ Deleted session {session_id} and its messages")
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete session")
    
    async def flush(self):
        """Force immediate persistence of all cached data."""
        await self._persist_dirty_data() 