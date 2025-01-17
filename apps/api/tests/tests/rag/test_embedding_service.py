import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import numpy as np
from src.memory.embeddings import EmbeddingService

@pytest.fixture
def mock_cache():
    with patch("src.memory.embeddings.Cache") as mock:
        cache = AsyncMock()
        mock.return_value = cache
        yield cache

@pytest.fixture
def mock_openai():
    with patch("src.memory.embeddings.openai") as mock:
        mock.Embedding.create = AsyncMock()
        yield mock

@pytest.fixture
def embedding_service(mock_cache, mock_openai):
    return EmbeddingService()

@pytest.mark.asyncio
class TestEmbeddingService:
    async def test_generate_embedding_success(self, embedding_service, mock_openai):
        """Tests successful embedding generation."""
        # Setup
        text = "Test text"
        mock_embedding = [0.1, 0.2, 0.3]
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": mock_embedding}]
        }

        # Execute
        result = await embedding_service.generate_embedding(text)

        # Verify
        assert result == mock_embedding
        mock_openai.Embedding.create.assert_called_once_with(
            input=text,
            model="text-embedding-3-large"
        )

    async def test_generate_embedding_with_cache_hit(self, embedding_service, mock_cache, mock_openai):
        """Tests embedding generation with cache hit."""
        # Setup
        text = "Test text"
        cached_embedding = [0.1, 0.2, 0.3]
        mock_cache.get.return_value = cached_embedding

        # Execute
        result = await embedding_service.generate_embedding(text)

        # Verify
        assert result == cached_embedding
        mock_cache.get.assert_called_once()
        mock_openai.Embedding.create.assert_not_called()

    async def test_generate_embedding_with_cache_miss(self, embedding_service, mock_cache, mock_openai):
        """Tests embedding generation with cache miss."""
        # Setup
        text = "Test text"
        mock_embedding = [0.1, 0.2, 0.3]
        mock_cache.get.return_value = None
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": mock_embedding}]
        }

        # Execute
        result = await embedding_service.generate_embedding(text)

        # Verify
        assert result == mock_embedding
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once_with(
            f"embedding:{hash(text)}",
            mock_embedding,
            ttl=3600 * 24  # 24 hours
        )

    async def test_generate_embedding_failure(self, embedding_service, mock_openai):
        """Tests embedding generation failure."""
        # Setup
        mock_openai.Embedding.create.side_effect = Exception("API error")

        # Execute and verify
        with pytest.raises(Exception):
            await embedding_service.generate_embedding("test")

    async def test_generate_batch_embeddings_success(self, embedding_service, mock_openai):
        """Tests successful batch embedding generation."""
        # Setup
        texts = ["Text 1", "Text 2"]
        mock_embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": emb} for emb in mock_embeddings]
        }

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Verify
        assert results == mock_embeddings
        mock_openai.Embedding.create.assert_called_once_with(
            input=texts,
            model="text-embedding-3-large"
        )

    async def test_generate_batch_embeddings_with_cache(self, embedding_service, mock_cache, mock_openai):
        """Tests batch embedding generation with partial cache hits."""
        # Setup
        texts = ["Text 1", "Text 2"]
        cached_embedding = [0.1, 0.2]
        new_embedding = [0.3, 0.4]
        
        # First text is cached, second isn't
        mock_cache.get.side_effect = [cached_embedding, None]
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": new_embedding}]
        }

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Verify
        assert results == [cached_embedding, new_embedding]
        assert mock_cache.get.call_count == 2
        mock_openai.Embedding.create.assert_called_once()
        mock_cache.set.assert_called_once()

    async def test_generate_batch_embeddings_failure(self, embedding_service, mock_openai):
        """Tests batch embedding generation failure."""
        # Setup
        mock_openai.Embedding.create.side_effect = Exception("API error")

        # Execute and verify
        with pytest.raises(Exception):
            await embedding_service.generate_batch_embeddings(["test1", "test2"])

    async def test_empty_input(self, embedding_service):
        """Tests handling of empty input."""
        # Test empty string
        with pytest.raises(ValueError):
            await embedding_service.generate_embedding("")

        # Test empty batch
        with pytest.raises(ValueError):
            await embedding_service.generate_batch_embeddings([])

    async def test_invalid_input(self, embedding_service):
        """Tests handling of invalid input."""
        # Test None
        with pytest.raises(ValueError):
            await embedding_service.generate_embedding(None)

        # Test invalid types
        with pytest.raises(TypeError):
            await embedding_service.generate_embedding(123)

        with pytest.raises(TypeError):
            await embedding_service.generate_batch_embeddings("not a list")

    async def test_normalize_text(self, embedding_service):
        """Tests text normalization."""
        # Setup
        text = "  Test   with   extra   spaces  \n\n"
        mock_openai.Embedding.create.return_value = {
            "data": [{"embedding": [0.1]}]
        }

        # Execute
        await embedding_service.generate_embedding(text)

        # Verify normalized text was used
        called_text = mock_openai.Embedding.create.call_args[1]["input"]
        assert called_text == "Test with extra spaces" 