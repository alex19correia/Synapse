import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from src.memory.rag import RAGSystem

@pytest.fixture
def mock_supabase():
    with patch("src.memory.rag.create_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_embedding_service():
    with patch("src.memory.rag.EmbeddingService") as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

@pytest.fixture
def rag_system(mock_supabase, mock_embedding_service):
    return RAGSystem()

@pytest.mark.asyncio
class TestRAGSystem:
    async def test_index_document_success(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests successful document indexing."""
        # Setup
        text = "This is a test document"
        metadata = {"source": "test", "type": "article"}
        mock_embedding = [0.1, 0.2, 0.3]
        mock_embedding_service.generate_embedding.return_value = mock_embedding
        mock_supabase.table().insert().execute.return_value.data = [{"id": 1}]

        # Execute
        result = await rag_system.index_document(text, metadata)

        # Verify
        assert result is True
        mock_embedding_service.generate_embedding.assert_called_once_with(text)
        mock_supabase.table().insert().execute.assert_called_once()
        
        # Verify correct data was inserted
        insert_data = mock_supabase.table().insert().execute.call_args[0][0]
        assert insert_data["content"] == text
        assert insert_data["embedding"] == mock_embedding
        assert insert_data["metadata"] == metadata
        assert "created_at" in insert_data

    async def test_index_document_failure_embedding(self, rag_system, mock_embedding_service):
        """Tests document indexing with embedding generation failure."""
        # Setup
        mock_embedding_service.generate_embedding.side_effect = Exception("Embedding failed")

        # Execute
        result = await rag_system.index_document("test", {})

        # Verify
        assert result is False
        mock_embedding_service.generate_embedding.assert_called_once()

    async def test_index_document_failure_insert(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests document indexing with database insert failure."""
        # Setup
        mock_embedding_service.generate_embedding.return_value = [0.1]
        mock_supabase.table().insert().execute.return_value.data = None

        # Execute
        result = await rag_system.index_document("test", {})

        # Verify
        assert result is False
        mock_supabase.table().insert().execute.assert_called_once()

    async def test_search_similar_success(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests successful similar document search."""
        # Setup
        query = "test query"
        mock_embedding = [0.1, 0.2, 0.3]
        mock_docs = [
            {"content": "doc1", "similarity": 0.9},
            {"content": "doc2", "similarity": 0.8}
        ]
        
        mock_embedding_service.generate_embedding.return_value = mock_embedding
        mock_supabase.rpc().execute.return_value.data = mock_docs

        # Execute
        results = await rag_system.search_similar(query, limit=2)

        # Verify
        assert results == mock_docs
        mock_embedding_service.generate_embedding.assert_called_once_with(query)
        mock_supabase.rpc.assert_called_once_with(
            'match_documents',
            {
                'query_embedding': mock_embedding,
                'match_threshold': 0.7,
                'match_count': 2
            }
        )

    async def test_search_similar_failure_embedding(self, rag_system, mock_embedding_service):
        """Tests similar document search with embedding generation failure."""
        # Setup
        mock_embedding_service.generate_embedding.side_effect = Exception("Embedding failed")

        # Execute
        results = await rag_system.search_similar("test")

        # Verify
        assert results == []
        mock_embedding_service.generate_embedding.assert_called_once()

    async def test_search_similar_failure_search(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests similar document search with search failure."""
        # Setup
        mock_embedding_service.generate_embedding.return_value = [0.1]
        mock_supabase.rpc().execute.side_effect = Exception("Search failed")

        # Execute
        results = await rag_system.search_similar("test")

        # Verify
        assert results == []
        mock_supabase.rpc.assert_called_once()

    async def test_get_context_success(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests successful context retrieval."""
        # Setup
        query = "test query"
        mock_docs = [
            {"content": "First relevant document"},
            {"content": "Second relevant document"}
        ]
        mock_embedding_service.generate_embedding.return_value = [0.1]
        mock_supabase.rpc().execute.return_value.data = mock_docs

        # Execute
        context = await rag_system.get_context(query)

        # Verify
        expected_context = "First relevant document\n\nSecond relevant document"
        assert context == expected_context
        mock_embedding_service.generate_embedding.assert_called_once_with(query)

    async def test_get_context_no_results(self, rag_system, mock_supabase, mock_embedding_service):
        """Tests context retrieval with no matching documents."""
        # Setup
        mock_embedding_service.generate_embedding.return_value = [0.1]
        mock_supabase.rpc().execute.return_value.data = []

        # Execute
        context = await rag_system.get_context("test")

        # Verify
        assert context == ""
        mock_embedding_service.generate_embedding.assert_called_once()

    async def test_get_context_failure(self, rag_system, mock_embedding_service):
        """Tests context retrieval with search failure."""
        # Setup
        mock_embedding_service.generate_embedding.side_effect = Exception("Search failed")

        # Execute
        context = await rag_system.get_context("test")

        # Verify
        assert context == ""
        mock_embedding_service.generate_embedding.assert_called_once() 