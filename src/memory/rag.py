"""RAG system module."""
import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from datetime import datetime
import numpy as np
from rich.console import Console
from .embeddings import EmbeddingService
from src.config.settings import Settings

console = Console()

class RAGSystem:
    """Retrieval Augmented Generation System"""
    
    def __init__(self, settings: Settings):
        """Initialize RAG system with settings."""
        self.supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        self.embedding_service = EmbeddingService()
        
    async def index_document(self, text: str, metadata: Dict) -> bool:
        """Index a document in the vector store.
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding = await self.embedding_service.generate_embedding(text)
            
            # Insert into Supabase
            data = {
                "content": text,
                "embedding": embedding,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("documents").insert(data).execute()
            return True if result.data else False
            
        except Exception as e:
            console.print(f"[error]Error indexing document: {e}[/error]")
            return False
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar documents based on query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of similar documents
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Perform similarity search
            result = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.7,
                    'match_count': limit
                }
            ).execute()
            
            return result.data
            
        except Exception as e:
            console.print(f"[error]Search error: {e}[/error]")
            return []
    
    async def query(self, query: str) -> Dict[str, str]:
        """Query the RAG system.
        
        Args:
            query: User query
            
        Returns:
            Dict with response and context
        """
        context = await self.get_context(query)
        return {
            "response": f"Here is the relevant context:\n\n{context}",
            "context": context
        }
    
    async def get_context(self, query: str) -> str:
        """Get relevant context for a query.
        
        Args:
            query: Search query
            
        Returns:
            Concatenated relevant documents
        """
        documents = await self.search_similar(query)
        
        if not documents:
            return ""
            
        # Concatenate relevant documents
        context = "\n\n".join([doc["content"] for doc in documents])
        return context