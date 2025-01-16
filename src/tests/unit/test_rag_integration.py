"""Tests for the RAG integration module."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from src.crawlers.rag_integration import RAGProcessor, Document
from src.analytics.metrics.crawler_metrics import CrawlerMetrics

@pytest.fixture
def mock_metrics():
    """Fixture for mocked metrics."""
    metrics = AsyncMock(spec=CrawlerMetrics)
    metrics.observe_duration = AsyncMock()
    metrics.track_page = AsyncMock()
    return metrics

@pytest.fixture
def sample_documents():
    """Fixture for sample documents."""
    return [
        Document(
            content="Test document 1",
            metadata={"source": "test1"},
            timestamp=datetime.now()
        ),
        Document(
            content="Test document 2",
            metadata={"source": "test2"},
            timestamp=datetime.now()
        )
    ]

@pytest.fixture
async def processor(mock_metrics):
    """Fixture for RAG processor with mocked dependencies."""
    with patch('src.crawlers.rag_integration.CrawlerMetrics', return_value=mock_metrics):
        processor = RAGProcessor()
        yield processor

@pytest.mark.asyncio
async def test_initialization():
    """Test RAG processor initialization."""
    processor = RAGProcessor()
    assert isinstance(processor.metrics, CrawlerMetrics)

@pytest.mark.asyncio
async def test_process_documents_success(processor, sample_documents, mock_metrics):
    """Test successful document processing."""
    result = await processor.process_documents(sample_documents)
    
    assert result['success'] is True
    assert result['documents'] == 2
    assert result['chunks'] == 2
    assert result['embeddings'] == 2
    assert result['vectors'] == 2
    assert isinstance(result['duration'], float)
    
    mock_metrics.observe_duration.assert_awaited_once()
    mock_metrics.track_page.assert_awaited_once_with(status='success')

@pytest.mark.asyncio
async def test_process_documents_empty(processor, mock_metrics):
    """Test processing empty document list."""
    result = await processor.process_documents([])
    
    assert result['success'] is True
    assert result['documents'] == 0
    assert result['chunks'] == 0
    assert result['embeddings'] == 0
    assert result['vectors'] == 0

@pytest.mark.asyncio
async def test_process_documents_error(processor, sample_documents, mock_metrics):
    """Test error handling during document processing."""
    with patch.object(processor, '_chunk_documents', side_effect=Exception("Chunking error")):
        result = await processor.process_documents(sample_documents)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Chunking error' in result['error']
        mock_metrics.track_page.assert_awaited_once_with(status='error')

@pytest.mark.asyncio
async def test_chunk_documents(processor, sample_documents):
    """Test document chunking."""
    chunks = await processor._chunk_documents(sample_documents)
    
    assert len(chunks) == 2
    assert chunks[0] == sample_documents[0].content
    assert chunks[1] == sample_documents[1].content

@pytest.mark.asyncio
async def test_generate_embeddings(processor):
    """Test embedding generation."""
    chunks = ["Test chunk 1", "Test chunk 2"]
    embeddings = await processor._generate_embeddings(chunks)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 768  # Default embedding size
    assert all(isinstance(x, float) for x in embeddings[0])

@pytest.mark.asyncio
async def test_store_vectors(processor):
    """Test vector storage."""
    embeddings = [[0.0] * 768 for _ in range(2)]
    vectors = await processor._store_vectors(embeddings)
    
    assert len(vectors) == 2
    assert all(isinstance(x, str) for x in vectors)
    assert vectors[0].startswith("vector_")

@pytest.mark.asyncio
async def test_document_model():
    """Test Document model validation."""
    doc = Document(content="Test content")
    
    assert doc.content == "Test content"
    assert isinstance(doc.metadata, dict)
    assert isinstance(doc.timestamp, datetime)

@pytest.mark.asyncio
async def test_metrics_integration(processor, sample_documents, mock_metrics):
    """Test metrics integration during processing."""
    # Mock datetime.now() to return different times
    start_time = datetime(2024, 1, 14, 12, 0, 0)
    end_time = start_time + timedelta(seconds=1)
    
    with patch('src.crawlers.rag_integration.datetime') as mock_datetime:
        mock_datetime.now.side_effect = [start_time, end_time]
        await processor.process_documents(sample_documents)
    
    # Verify metrics were tracked
    assert mock_metrics.observe_duration.await_count == 1
    assert mock_metrics.track_page.await_count == 1
    
    # Verify duration was 1 second
    duration_call = mock_metrics.observe_duration.await_args[0][0]
    assert duration_call == 1.0 