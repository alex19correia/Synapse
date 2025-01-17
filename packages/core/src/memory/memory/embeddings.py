from typing import List, Dict, Optional
from openai import OpenAI
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from rich.console import Console

console = Console()

class EmbeddingService:
    """Serviço de geração e gestão de embeddings"""
    
    def __init__(self):
        self.client = OpenAI()
        self.model = "text-embedding-3-large"
        self.dimensions = 3072  # Dimensões do modelo atual
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            console.print(f"[error]Erro ao gerar embedding: {e}[/error]")
            raise
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos"""
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings 