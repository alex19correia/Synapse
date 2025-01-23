"""Enhanced RAG system with multi-vector support."""
from enum import Enum
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
from supabase import create_client, Client
from rich.console import Console
from sklearn.feature_extraction.text import TfidfVectorizer
from .embeddings import EmbeddingService
from src.config.settings import Settings

console = Console()

class EmbeddingType(Enum):
    """Types of embeddings supported by the system."""
    SEMANTIC = "semantic"  # OpenAI embeddings for semantic understanding
    KEYWORD = "keyword"    # TF-IDF for keyword matching
    CODE = "code"         # Specialized for code understanding

@dataclass
class SearchResult:
    """Search result with combined scores."""
    content: str
    metadata: Dict
    scores: Dict[EmbeddingType, float]
    combined_score: float

@dataclass
class IndexStats:
    """Statistics about index usage."""
    index_name: str
    total_scans: int
    avg_scan_time: float
    size_bytes: int
    last_vacuum: datetime

class EnhancedRAGSystem:
    """Enhanced RAG system with multi-vector support."""
    
    def __init__(
        self,
        settings: Settings,
        weights: Optional[Dict[EmbeddingType, float]] = None
    ):
        """Initialize enhanced RAG system.
        
        Args:
            settings: Application settings
            weights: Optional weights for different embedding types
        """
        self.supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        self.embedding_service = EmbeddingService()
        self.tfidf = TfidfVectorizer()
        self.weights = weights or {
            EmbeddingType.SEMANTIC: 0.6,
            EmbeddingType.KEYWORD: 0.3,
            EmbeddingType.CODE: 0.1
        }
        
    async def process_and_store_document(
        self,
        content: str,
        metadata: Dict,
        embedding_types: Optional[List[EmbeddingType]] = None
    ) -> bool:
        """Process and store document with multiple embedding types.
        
        Args:
            content: Document content
            metadata: Document metadata
            embedding_types: Types of embeddings to generate
            
        Returns:
            True if successful
        """
        try:
            # Default to all embedding types if none specified
            embedding_types = embedding_types or list(EmbeddingType)
            
            embeddings = {}
            
            # Generate embeddings for each type
            for emb_type in embedding_types:
                if emb_type == EmbeddingType.SEMANTIC:
                    # OpenAI embeddings for semantic understanding
                    embedding = await self.embedding_service.generate_embedding(content)
                elif emb_type == EmbeddingType.KEYWORD:
                    # TF-IDF for keyword matching
                    tfidf_matrix = self.tfidf.fit_transform([content])
                    embedding = tfidf_matrix.toarray()[0]
                elif emb_type == EmbeddingType.CODE:
                    # For now, use semantic embeddings for code
                    # TODO: Implement specialized code embeddings
                    embedding = await self.embedding_service.generate_embedding(content)
                
                embeddings[emb_type.value] = embedding.tolist()
            
            # Store in Supabase
            data = {
                "content": content,
                "embeddings": embeddings,
                "metadata": {
                    **metadata,
                    "embedding_types": [et.value for et in embedding_types]
                },
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("enhanced_documents").insert(data).execute()
            return True if result.data else False
            
        except Exception as e:
            console.print(f"[error]Error processing document: {e}[/error]")
            return False
    
    async def retrieve_relevant_documentation(
        self,
        query: str,
        limit: int = 5,
        embedding_types: Optional[List[EmbeddingType]] = None,
        weights: Optional[Dict[EmbeddingType, float]] = None
    ) -> List[SearchResult]:
        """Retrieve relevant documentation using multi-vector search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            embedding_types: Types of embeddings to use
            weights: Custom weights for different embedding types
            
        Returns:
            List of search results with combined scores
        """
        try:
            # Use specified types or all available
            embedding_types = embedding_types or list(EmbeddingType)
            weights = weights or self.weights
            
            # Generate query embeddings
            query_embeddings = {}
            for emb_type in embedding_types:
                if emb_type == EmbeddingType.SEMANTIC:
                    embedding = await self.embedding_service.generate_embedding(query)
                elif emb_type == EmbeddingType.KEYWORD:
                    tfidf_matrix = self.tfidf.transform([query])
                    embedding = tfidf_matrix.toarray()[0]
                elif emb_type == EmbeddingType.CODE:
                    embedding = await self.embedding_service.generate_embedding(query)
                    
                query_embeddings[emb_type.value] = embedding
            
            # Search for each embedding type
            all_results = {}
            for emb_type in embedding_types:
                result = self.supabase.rpc(
                    'match_enhanced_documents',
                    {
                        'query_embedding': query_embeddings[emb_type.value],
                        'embedding_type': emb_type.value,
                        'match_threshold': 0.5,
                        'match_count': limit
                    }
                ).execute()
                
                all_results[emb_type] = result.data
            
            # Combine and score results
            combined_results = self._combine_search_results(
                all_results,
                weights,
                limit
            )
            
            return combined_results
            
        except Exception as e:
            console.print(f"[error]Search error: {e}[/error]")
            return []
    
    def _combine_search_results(
        self,
        results: Dict[EmbeddingType, List[Dict]],
        weights: Dict[EmbeddingType, float],
        limit: int
    ) -> List[SearchResult]:
        """Combine results from different embedding types.
        
        Args:
            results: Results from each embedding type
            weights: Weights for different embedding types
            limit: Maximum number of results
            
        Returns:
            Combined and scored results
        """
        # Combine all document IDs
        all_docs = {}
        
        # Collect scores for each document
        for emb_type, docs in results.items():
            for doc in docs:
                doc_id = doc["id"]
                if doc_id not in all_docs:
                    all_docs[doc_id] = {
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "scores": {}
                    }
                all_docs[doc_id]["scores"][emb_type] = doc["similarity"]
        
        # Calculate combined scores
        scored_results = []
        for doc_id, doc in all_docs.items():
            combined_score = sum(
                doc["scores"].get(et, 0) * weights.get(et, 0)
                for et in EmbeddingType
            )
            
            scored_results.append(SearchResult(
                content=doc["content"],
                metadata=doc["metadata"],
                scores=doc["scores"],
                combined_score=combined_score
            ))
        
        # Sort by combined score and limit results
        scored_results.sort(key=lambda x: x.combined_score, reverse=True)
        return scored_results[:limit]

    async def get_index_stats(self) -> Dict[str, IndexStats]:
        """Get statistics about vector index usage."""
        try:
            # Query index statistics
            result = self.supabase.rpc(
                'get_index_stats',
                {}
            ).execute()
            
            stats = {}
            for row in result.data:
                stats[row['index_name']] = IndexStats(
                    index_name=row['index_name'],
                    total_scans=row['total_scans'],
                    avg_scan_time=row['avg_scan_time'],
                    size_bytes=row['size_bytes'],
                    last_vacuum=datetime.fromisoformat(row['last_vacuum'])
                )
            
            return stats
            
        except Exception as e:
            console.print(f"[error]Error getting index stats: {e}[/error]")
            return {}

    async def analyze_query_performance(
        self,
        query: str,
        embedding_type: EmbeddingType
    ) -> Dict:
        """Analyze query performance for a specific embedding type."""
        try:
            # Generate query embedding
            if embedding_type == EmbeddingType.SEMANTIC:
                embedding = await self.embedding_service.generate_embedding(query)
            elif embedding_type == EmbeddingType.KEYWORD:
                tfidf_matrix = self.tfidf.transform([query])
                embedding = tfidf_matrix.toarray()[0]
            else:
                embedding = await self.embedding_service.generate_embedding(query)
            
            # Get query plan
            result = self.supabase.rpc(
                'analyze_vector_query',
                {
                    'query_embedding': embedding.tolist(),
                    'embedding_type': embedding_type.value
                }
            ).execute()
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            console.print(f"[error]Error analyzing query: {e}[/error]")
            return {} 