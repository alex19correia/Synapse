"""
Text chunking utilities for RAG system.
"""
from typing import List
import re

class TextChunker:
    """Text chunker for RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize text chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is shorter than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [text]
            
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk of text
            end = start + self.chunk_size
            
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - self.chunk_overlap
                
            # Get actual chunk
            chunk = text[start:end]
            
            # If not at the end, try to break at sentence or word boundary
            if end < len(text):
                # Try to break at sentence boundary
                last_period = chunk.rfind('.')
                last_question = chunk.rfind('?')
                last_exclamation = chunk.rfind('!')
                
                sentence_end = max(last_period, last_question, last_exclamation)
                
                if sentence_end > self.chunk_size * 0.7:  # Only break at sentence if reasonably far along
                    end = start + sentence_end + 1
                    chunk = text[start:end]
                else:
                    # Break at word boundary
                    last_space = chunk.rfind(' ')
                    if last_space > 0:
                        end = start + last_space + 1
                        chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end
            
        return chunks 