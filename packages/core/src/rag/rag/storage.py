"""Vector store implementation."""
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Search result from vector store."""
    content: str
    metadata: Dict[str, str]
    score: float

class VectorStore:
    """Vector store for document embeddings."""
    
    def __init__(self, embedding_generator):
        """Initialize vector store."""
        self.embedding_generator = embedding_generator
        self.documents: List[str] = []
        self.metadata: List[Dict[str, str]] = []
        self.embeddings: List[np.ndarray] = []
        
    async def add_document(self, content: str, metadata: Optional[Dict[str, str]] = None) -> None:
        """
        Add document to vector store.
        
        Args:
            content: Document content
            metadata: Optional document metadata
        """
        # Generate embedding
        embedding = await self.embedding_generator.generate(content)
        
        # Store document
        self.documents.append(content)
        self.metadata.append(metadata or {})
        self.embeddings.append(embedding)
        
    async def search(
        self,
        query: str,
        limit: int = 2,
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        # For test mode, return mock results
        if len(self.documents) == 0:
            return []
            
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate(query)
        
        # Calculate similarities
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = np.dot(query_embedding, doc_embedding)
            similarities.append(similarity)
            
        # Get top results
        indices = np.argsort(similarities)[-limit:]
        
        # Format results
        results = []
        for idx in indices:
            if similarities[idx] >= score_threshold:
                results.append(SearchResult(
                    content=self.documents[idx],
                    metadata=self.metadata[idx],
                    score=float(similarities[idx])
                ))
                
        return results 