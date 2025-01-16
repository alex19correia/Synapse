from qdrant_client import QdrantClient
from src.config.settings import settings

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT
        )

    def create_collection(self, collection_name: str, vector_size: int = 768):
        """Cria uma nova collection no Qdrant"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "size": vector_size,
                    "distance": "Cosine"
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao criar collection: {e}")
            return False 