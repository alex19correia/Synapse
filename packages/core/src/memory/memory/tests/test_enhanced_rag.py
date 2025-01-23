"""Tests for enhanced RAG system with multi-vector support."""
import pytest
from typing import Dict
import numpy as np
from unittest.mock import Mock, patch
from ...memory.enhanced_rag import EnhancedRAGSystem, EmbeddingType, SearchResult
from src.config.settings import Settings

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        SUPABASE_URL="http://test.supabase.co",
        SUPABASE_KEY="test-key",
        OPENAI_API_KEY="test-key"
    )

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    return Mock()

@pytest.fixture
def enhanced_rag(mock_settings, mock_supabase):
    """Enhanced RAG system for testing."""
    with patch("supabase.create_client", return_value=mock_supabase):
        return EnhancedRAGSystem(mock_settings)

@pytest.mark.asyncio
async def test_process_document_all_embeddings(enhanced_rag, mock_supabase):
    """Test processing document with all embedding types."""
    # Mock embedding generation
    async def mock_generate_embedding(text):
        return np.random.rand(1536)
    
    enhanced_rag.embedding_service.generate_embedding = mock_generate_embedding
    
    # Test document
    content = "def test_function():\n    return 'Hello World'"
    metadata = {"type": "code", "language": "python"}
    
    # Process document
    success = await enhanced_rag.process_and_store_document(content, metadata)
    
    # Verify
    assert success
    mock_supabase.table.assert_called_with("enhanced_documents")
    insert_data = mock_supabase.table().insert.call_args[0][0]
    
    assert "semantic" in insert_data["embeddings"]
    assert "keyword" in insert_data["embeddings"]
    assert "code" in insert_data["embeddings"]
    assert insert_data["content"] == content
    assert insert_data["metadata"]["type"] == "code"

@pytest.mark.asyncio
async def test_retrieve_documentation_combined_scores(enhanced_rag, mock_supabase):
    """Test retrieving documentation with combined scores."""
    # Mock query embeddings
    async def mock_generate_embedding(text):
        return np.random.rand(1536)
    
    enhanced_rag.embedding_service.generate_embedding = mock_generate_embedding
    
    # Mock search results
    mock_results = {
        "semantic": [
            {"id": "1", "content": "Test content", "metadata": {}, "similarity": 0.8}
        ],
        "keyword": [
            {"id": "1", "content": "Test content", "metadata": {}, "similarity": 0.7}
        ],
        "code": [
            {"id": "1", "content": "Test content", "metadata": {}, "similarity": 0.6}
        ]
    }
    
    def mock_execute():
        return Mock(data=mock_results[mock_supabase.rpc.call_args[0][1]["embedding_type"]])
    
    mock_supabase.rpc().execute = mock_execute
    
    # Test retrieval
    results = await enhanced_rag.retrieve_relevant_documentation(
        "test query",
        limit=1
    )
    
    # Verify
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, SearchResult)
    assert result.content == "Test content"
    assert result.scores[EmbeddingType.SEMANTIC] == 0.8
    assert result.scores[EmbeddingType.KEYWORD] == 0.7
    assert result.scores[EmbeddingType.CODE] == 0.6
    
    # Verify combined score calculation
    expected_score = (
        0.8 * enhanced_rag.weights[EmbeddingType.SEMANTIC] +
        0.7 * enhanced_rag.weights[EmbeddingType.KEYWORD] +
        0.6 * enhanced_rag.weights[EmbeddingType.CODE]
    )
    assert result.combined_score == pytest.approx(expected_score)

@pytest.mark.asyncio
async def test_custom_weights(enhanced_rag, mock_supabase):
    """Test retrieval with custom weights."""
    # Mock embeddings and results
    async def mock_generate_embedding(text):
        return np.random.rand(1536)
    
    enhanced_rag.embedding_service.generate_embedding = mock_generate_embedding
    
    mock_results = {
        "semantic": [
            {"id": "1", "content": "Test content", "metadata": {}, "similarity": 0.8}
        ]
    }
    
    def mock_execute():
        return Mock(data=mock_results[mock_supabase.rpc.call_args[0][1]["embedding_type"]])
    
    mock_supabase.rpc().execute = mock_execute
    
    # Test with custom weights
    custom_weights = {EmbeddingType.SEMANTIC: 1.0}
    results = await enhanced_rag.retrieve_relevant_documentation(
        "test query",
        embedding_types=[EmbeddingType.SEMANTIC],
        weights=custom_weights
    )
    
    # Verify
    assert len(results) == 1
    result = results[0]
    assert result.combined_score == pytest.approx(0.8)  # Only semantic score

@pytest.mark.asyncio
async def test_error_handling(enhanced_rag, mock_supabase):
    """Test error handling in document processing and retrieval."""
    # Mock failure
    mock_supabase.table().insert.side_effect = Exception("Database error")
    
    # Test document processing error
    success = await enhanced_rag.process_and_store_document(
        "test content",
        {"type": "test"}
    )
    assert not success
    
    # Test retrieval error
    mock_supabase.rpc().execute.side_effect = Exception("Search error")
    results = await enhanced_rag.retrieve_relevant_documentation("test query")
    assert len(results) == 0

@pytest.mark.asyncio
async def test_vector_column_updates(enhanced_rag, mock_supabase):
    """Test that vector columns are properly updated."""
    # Mock embedding generation
    async def mock_generate_embedding(text):
        return np.array([0.1] * 1536)  # Fixed vector for testing
    
    enhanced_rag.embedding_service.generate_embedding = mock_generate_embedding
    
    # Test document
    content = "Test vector updates"
    metadata = {"type": "test"}
    
    # Process document
    success = await enhanced_rag.process_and_store_document(content, metadata)
    
    # Verify
    assert success
    insert_data = mock_supabase.table().insert.call_args[0][0]
    
    # Check that embeddings are properly formatted for vector columns
    semantic_vector = np.array(insert_data["embeddings"]["semantic"])
    assert semantic_vector.shape == (1536,)
    assert np.allclose(semantic_vector, np.array([0.1] * 1536))

@pytest.mark.asyncio
async def test_index_performance(enhanced_rag, mock_supabase):
    """Test index usage in queries."""
    # Mock query execution
    def mock_execute():
        return Mock(data=[{
            "id": "1",
            "content": "Test content",
            "metadata": {"type": "test"},
            "similarity": 0.9,
            "query_plan": "Index Scan using idx_semantic_vector"  # Simulated query plan
        }])
    
    mock_supabase.rpc().execute = mock_execute
    
    # Test query
    results = await enhanced_rag.retrieve_relevant_documentation(
        "test query",
        embedding_types=[EmbeddingType.SEMANTIC]
    )
    
    # Verify results
    assert len(results) == 1
    assert results[0].combined_score == pytest.approx(0.9)
    
    # In real implementation, we would verify index usage through EXPLAIN ANALYZE 