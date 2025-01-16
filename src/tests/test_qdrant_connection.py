import pytest
from qdrant_client import QdrantClient
from src.config import settings

@pytest.fixture
def qdrant_client():
    """Fixture para criar e gerenciar a conexão com o Qdrant"""
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=settings.QDRANT_TIMEOUT
    )
    yield client
    client.close()

def test_qdrant_connection(qdrant_client):
    """Testa a conexão básica com o Qdrant"""
    # Verifica se o cliente está ativo
    assert qdrant_client is not None
    
    # Testa a conexão com uma operação simples
    collections = qdrant_client.get_collections()
    assert isinstance(collections.collections, list) 