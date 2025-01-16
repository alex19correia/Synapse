"""Message service for managing chat messages."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from loguru import logger

from ..models.message import Message, MessageRole
from ..exceptions import MessageValidationError, DatabaseError

class MessageService:
    """Service for managing chat messages."""
    
    def __init__(self, db):
        """Initialize the message service with a database connection."""
        self.db = db
        logger.debug("🔧 MessageService initialized")
        
    async def save_message(self, message: Message) -> Dict[str, Any]:
        """
        Save a message to the database.
        
        Args:
            message: The message to save
            
        Returns:
            Dict[str, Any]: The saved message data
            
        Raises:
            MessageValidationError: If the message is invalid
            DatabaseError: If there's an error saving to the database
        """
        # Validate message
        if not message.content:
            raise MessageValidationError("Message content cannot be empty")
        if len(message.content) > 10000:
            raise MessageValidationError("Message content too long (max 10000 characters)")
            
        try:
            result = await self.db.table("messages").insert(
                message.model_dump()
            ).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise DatabaseError(f"Failed to save message: {e}")
        
    async def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Message]:
        """
        Get all messages for a session.
        
        Args:
            session_id: The session ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List[Message]: List of messages
            
        Raises:
            DatabaseError: If there's an error retrieving from the database
        """
        try:
            query = self.db.table("messages").select().where(
                "session_id", "=", session_id
            ).order_by("timestamp", "asc")
            
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
                
            result = await query.execute()
            return [Message(**msg) for msg in result.data]
        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            raise DatabaseError(f"Failed to get session messages: {e}")
            
    async def update_message(self, message_id: str, content: str) -> Dict[str, Any]:
        """
        Update a message's content.
        
        Args:
            message_id: The message ID
            content: The new content
            
        Returns:
            Dict[str, Any]: The updated message data
            
        Raises:
            MessageValidationError: If the content is invalid
            DatabaseError: If there's an error updating the database
        """
        if not content:
            raise MessageValidationError("Message content cannot be empty")
        if len(content) > 10000:
            raise MessageValidationError("Message content too long (max 10000 characters)")
            
        try:
            result = await self.db.table("messages").update({
                "content": content,
                "updated_at": datetime.now(timezone.utc)
            }).where("id", "=", message_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            raise DatabaseError(f"Failed to update message: {e}")
            
    async def delete_message(self, message_id: str) -> Dict[str, Any]:
        """
        Delete a message.
        
        Args:
            message_id: The message ID
            
        Returns:
            Dict[str, Any]: The deleted message data
            
        Raises:
            DatabaseError: If there's an error deleting from the database
        """
        try:
            result = await self.db.table("messages").delete().where(
                "id", "=", message_id
            ).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise DatabaseError(f"Failed to delete message: {e}") 