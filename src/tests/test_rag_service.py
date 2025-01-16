import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.rag_service import RAGService
from src.config.llm_config import LLMConfig

@pytest.fixture
def mock_qdrant():
    return Mock()

@pytest.fixture
def rag_service(mock_qdrant):
    with patch('qdrant_client.QdrantClient', return_value=mock_qdrant):
        config = LLMConfig()
        return RAGService(config)

class TestRAGService:
    async def test_add_to_knowledge_base(self, rag_service, mock_qdrant):
        # Arrange
        text = "Test document"
        metadata = {"source": "test", "category": "unit_test"}
        embedding = [0.1] * 1536
        
        # Act
        result = await rag_service.add_to_knowledge_base(text, metadata, embedding)
        
        # Assert
        assert result == True
        mock_qdrant.upsert.assert_called_once()
        
    async def test_search_similar(self, rag_service, mock_qdrant):
        # Arrange
        query_embedding = [0.1] * 1536
        mock_qdrant.search.return_value = [
            Mock(
                payload={"text": "Test", "metadata": {"source": "test"}},
                score=0.95
            )
        ]
        
        # Act
        results = await rag_service.search_similar(query_embedding)
        
        # Assert
        assert len(results) == 1
        assert results[0]["score"] == 0.95
        assert "text" in results[0] 