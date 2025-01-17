import pytest
from unittest.mock import Mock, AsyncMock, patch

# Imports relativos ao pacote src
from src.crawlers.rag_integration import RAGProcessor
from src.crawlers.parallel_crawler import WebContent

# Fixtures
@pytest.fixture
def mock_metrics():
    metrics = Mock()
    metrics.track_rag_processing = AsyncMock()
    metrics.track_rag_error = AsyncMock()
    metrics.track_chunk_metrics = AsyncMock()
    metrics.track_embedding_duration = AsyncMock()
    return metrics

@pytest.fixture
def mock_chunker():
    chunker = Mock()
    chunker.chunk_document = AsyncMock(return_value=[
        Mock(text="Chunk 1", metadata={"index": 0}),
        Mock(text="Chunk 2", metadata={"index": 1})
    ])
    return chunker

@pytest.fixture
def mock_embedding_generator():
    generator = Mock()
    generator.generate_batch = AsyncMock(return_value=[
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ])
    return generator

@pytest.fixture
def mock_vector_store():
    store = Mock()
    store.add_documents = AsyncMock()
    return store

@pytest.fixture
def sample_content():
    return [
        WebContent(
            title="Test Page 1",
            content="Test content 1",
            url="https://test.com/1",
            metadata={"source": "test"}
        ),
        WebContent(
            title="Test Page 2",
            content="Test content 2",
            url="https://test.com/2",
            metadata={"source": "test"}
        )
    ]

# Testes
@pytest.mark.asyncio
async def test_process_crawled_content_success(
    mock_metrics,
    mock_chunker,
    mock_embedding_generator,
    mock_vector_store,
    sample_content
):
    """Testa processamento bem sucedido de conteúdo crawleado"""
    with patch("src.crawlers.rag_integration.CrawlerMetrics") as MockMetrics, \
         patch("src.crawlers.rag_integration.SemanticChunker") as MockChunker, \
         patch("src.crawlers.rag_integration.EmbeddingGenerator") as MockEmbedding, \
         patch("src.crawlers.rag_integration.VectorStore") as MockVectorStore:
        
        # Setup mocks
        MockMetrics.getInstance.return_value = mock_metrics
        MockChunker.return_value = mock_chunker
        MockEmbedding.return_value = mock_embedding_generator
        MockVectorStore.return_value = mock_vector_store
        
        # Executa processamento
        processor = RAGProcessor(chunk_size=512, chunk_overlap=50)
        metrics = await processor.process_crawled_content(sample_content)
        
        # Verifica resultado
        assert metrics["total_documents"] == len(sample_content)
        assert metrics["chunks_generated"] == 4  # 2 chunks por documento
        assert metrics["embeddings_generated"] == 4
        assert metrics["vectors_stored"] == 4
        
        # Verifica chamadas
        assert mock_chunker.chunk_document.call_count == len(sample_content)
        assert mock_embedding_generator.generate_batch.call_count == 1
        mock_vector_store.add_documents.assert_called_once()
        mock_metrics.track_rag_processing.assert_called_once()

@pytest.mark.asyncio
async def test_process_crawled_content_chunking_error(
    mock_metrics,
    mock_chunker,
    mock_embedding_generator,
    mock_vector_store,
    sample_content
):
    """Testa erro durante chunking"""
    mock_chunker.chunk_document.side_effect = Exception("Chunking error")
    
    with patch("src.crawlers.rag_integration.CrawlerMetrics") as MockMetrics, \
         patch("src.crawlers.rag_integration.SemanticChunker") as MockChunker, \
         patch("src.crawlers.rag_integration.EmbeddingGenerator") as MockEmbedding, \
         patch("src.crawlers.rag_integration.VectorStore") as MockVectorStore:
        
        MockMetrics.getInstance.return_value = mock_metrics
        MockChunker.return_value = mock_chunker
        MockEmbedding.return_value = mock_embedding_generator
        MockVectorStore.return_value = mock_vector_store
        
        processor = RAGProcessor()
        
        with pytest.raises(Exception) as exc_info:
            await processor.process_crawled_content(sample_content)
        
        assert str(exc_info.value) == "Chunking error"
        mock_metrics.track_rag_error.assert_called_once()
        mock_embedding_generator.generate_batch.assert_not_called()
        mock_vector_store.add_documents.assert_not_called()

@pytest.mark.asyncio
async def test_process_crawled_content_embedding_error(
    mock_metrics,
    mock_chunker,
    mock_embedding_generator,
    mock_vector_store,
    sample_content
):
    """Testa erro durante geração de embeddings"""
    mock_embedding_generator.generate_batch.side_effect = Exception("Embedding error")
    
    with patch("src.crawlers.rag_integration.CrawlerMetrics") as MockMetrics, \
         patch("src.crawlers.rag_integration.SemanticChunker") as MockChunker, \
         patch("src.crawlers.rag_integration.EmbeddingGenerator") as MockEmbedding, \
         patch("src.crawlers.rag_integration.VectorStore") as MockVectorStore:
        
        MockMetrics.getInstance.return_value = mock_metrics
        MockChunker.return_value = mock_chunker
        MockEmbedding.return_value = mock_embedding_generator
        MockVectorStore.return_value = mock_vector_store
        
        processor = RAGProcessor()
        
        with pytest.raises(Exception) as exc_info:
            await processor.process_crawled_content(sample_content)
        
        assert str(exc_info.value) == "Embedding error"
        mock_metrics.track_rag_error.assert_called_once()
        mock_vector_store.add_documents.assert_not_called()

@pytest.mark.asyncio
async def test_process_empty_content(
    mock_metrics,
    mock_chunker,
    mock_embedding_generator,
    mock_vector_store
):
    """Testa processamento de lista vazia"""
    with patch("src.crawlers.rag_integration.CrawlerMetrics") as MockMetrics, \
         patch("src.crawlers.rag_integration.SemanticChunker") as MockChunker, \
         patch("src.crawlers.rag_integration.EmbeddingGenerator") as MockEmbedding, \
         patch("src.crawlers.rag_integration.VectorStore") as MockVectorStore:
        
        MockMetrics.getInstance.return_value = mock_metrics
        MockChunker.return_value = mock_chunker
        MockEmbedding.return_value = mock_embedding_generator
        MockVectorStore.return_value = mock_vector_store
        
        processor = RAGProcessor()
        metrics = await processor.process_crawled_content([])
        
        assert metrics["total_documents"] == 0
        assert metrics["chunks_generated"] == 0
        assert metrics["embeddings_generated"] == 0
        assert metrics["vectors_stored"] == 0
        
        mock_chunker.chunk_document.assert_not_called()
        mock_embedding_generator.generate_batch.assert_not_called()
        mock_vector_store.add_documents.assert_not_called() 