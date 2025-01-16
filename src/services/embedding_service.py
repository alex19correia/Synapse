from typing import List, Optional
import numpy as np
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

class EmbeddingService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto usando OpenAI
        """
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
        
    async def get_batch_embeddings(
        self, 
        texts: List[str]
    ) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos
        """
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
        
    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calcula similaridade coseno entre dois embeddings
        """
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        ) 