"""Chat service module."""
from typing import Dict, Any, List, AsyncGenerator
from src.llm.llm_service import LLMService
from src.config.settings import Settings

class ChatService:
    """Chat service implementation."""
    
    def __init__(self, settings: Settings):
        """Initialize chat service."""
        self.llm = LLMService(settings)
        self.settings = settings
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant named Synapse. You have access to various services including Redis, Qdrant vector store, and Supabase database. You help users with their questions and tasks while maintaining context of the conversation."}
        ]
        
    async def chat(
        self,
        query: str,
        model: str = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """Process chat query."""
        # Add user message
        self.messages.append({"role": "user", "content": query})
        
        # Get response
        result = await self.llm.complete(self.messages, model)
        
        # Add assistant response to history
        self.messages.append({
            "role": "assistant", 
            "content": result["response"]
        })
        
        return result
        
    async def stream_chat(
        self,
        query: str,
        model: str = None,
        temperature: float = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat response."""
        # Add user message
        self.messages.append({"role": "user", "content": query})
        
        # Stream response
        response_chunks = []
        async for chunk in self.llm.stream(self.messages, model):
            response_chunks.append(chunk)
            yield chunk
            
        # Add complete response to history
        self.messages.append({
            "role": "assistant",
            "content": "".join(response_chunks)
        }) 