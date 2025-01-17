"""
Embeddings generator for RAG system.
"""
import numpy as np
from typing import List

class EmbeddingGenerator:
    """Generates embeddings for text."""
    
    def __init__(self, dimension: int = 384):
        """Initialize embedding generator."""
        self.dimension = dimension
        
    async def generate(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Text embedding
        """
        # For testing, return random embedding
        embedding = np.random.randn(self.dimension)
        return embedding / np.linalg.norm(embedding)
        
    async def generate_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: Texts to generate embeddings for
            
        Returns:
            List of text embeddings
        """
        return [await self.generate(text) for text in texts] 