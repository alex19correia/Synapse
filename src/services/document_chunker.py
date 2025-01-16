from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Chunk:
    text: str
    metadata: Dict
    start_idx: int
    end_idx: int
    chunk_id: str

class DocumentChunker:
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
    def chunk_document(self, text: str, metadata: Dict) -> List[Chunk]:
        """
        Divide documento em chunks com overlap
        """
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            # Calcula fim do chunk atual
            end_idx = min(start_idx + self.max_chunk_size, len(text))
            
            # Ajusta para não cortar palavras
            if end_idx < len(text):
                end_idx = self._find_sentence_boundary(text, end_idx)
                
            chunk_text = text[start_idx:end_idx]
            chunk_id = f"{metadata.get('doc_id', 'doc')}_{start_idx}"
            
            chunks.append(Chunk(
                text=chunk_text,
                metadata={
                    **metadata,
                    "chunk_id": chunk_id,
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                    "timestamp": datetime.now().isoformat()
                },
                start_idx=start_idx,
                end_idx=end_idx,
                chunk_id=chunk_id
            ))
            
            # Avança considerando overlap
            start_idx = end_idx - self.overlap
            
        return chunks
        
    def _find_sentence_boundary(self, text: str, position: int) -> int:
        """
        Encontra o fim da sentença mais próximo da posição
        """
        sentence_endings = '.!?'
        for i in range(position, max(position - 100, 0), -1):
            if text[i] in sentence_endings:
                return i + 1
        return position 