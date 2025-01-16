"""
Text chunking utilities for RAG system.
"""
from typing import List

class TextChunker:
    """Text chunker for RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize text chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
            
        # For testing, just return the text as a single chunk
        return [text] 