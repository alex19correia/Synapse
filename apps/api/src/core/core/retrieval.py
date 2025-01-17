class RetrievalSystem:
    def __init__(self):
        self.vector_store = None  # Será configurado com Qdrant
        
    def retrieve(self, query: str, k: int = 3):
        """Recupera documentos relevantes baseados na query"""
        pass 