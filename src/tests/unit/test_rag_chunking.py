"""Tests for the text chunking module."""

import pytest
from src.rag.chunking import TextChunker, TextChunk

@pytest.fixture
def chunker():
    """Fixture for TextChunker with default settings."""
    return TextChunker()

@pytest.fixture
def small_chunker():
    """Fixture for TextChunker with small chunks for testing."""
    return TextChunker(chunk_size=10, chunk_overlap=3)

def test_initialization():
    """Test chunker initialization with custom parameters."""
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 100

def test_empty_text(chunker):
    """Test chunking empty text."""
    chunks = chunker.split_text("")
    assert len(chunks) == 0

def test_text_smaller_than_chunk(chunker):
    """Test chunking text smaller than chunk size."""
    text = "Small text"
    chunks = chunker.split_text(text)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].metadata["start_char"] == 0
    assert chunks[0].metadata["end_char"] == len(text)

def test_text_with_multiple_chunks(small_chunker):
    """Test chunking text into multiple overlapping chunks."""
    text = "This is a longer text for testing chunks"
    chunks = small_chunker.split_text(text)
    
    # Verify number of chunks
    assert len(chunks) > 1
    
    # Verify first chunk
    assert chunks[0].text == "This is a "
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].metadata["start_char"] == 0
    assert chunks[0].metadata["end_char"] == 10
    
    # Verify overlap in second chunk
    assert chunks[1].text[0:3] == chunks[0].text[-3:]
    
    # Verify all chunks are proper TextChunk instances
    for chunk in chunks:
        assert isinstance(chunk, TextChunk)
        assert "chunk_index" in chunk.metadata
        assert "start_char" in chunk.metadata
        assert "end_char" in chunk.metadata

def test_custom_metadata(small_chunker):
    """Test chunking with custom metadata."""
    text = "Text for testing metadata"
    metadata = {"source": "test", "language": "en"}
    chunks = small_chunker.split_text(text, metadata)
    
    for chunk in chunks:
        assert chunk.metadata["source"] == "test"
        assert chunk.metadata["language"] == "en"
        assert "chunk_index" in chunk.metadata

def test_chunk_boundaries(small_chunker):
    """Test that chunk boundaries are correct."""
    text = "0123456789ABCDEFGHIJ"  # 20 characters
    chunks = small_chunker.split_text(text)
    
    # Verify each chunk's boundaries
    for i, chunk in enumerate(chunks):
        start = chunk.metadata["start_char"]
        end = chunk.metadata["end_char"]
        assert chunk.text == text[start:end]
        assert len(chunk.text) <= small_chunker.chunk_size

def test_chunk_overlap_consistency(small_chunker):
    """Test that chunk overlap is consistent."""
    text = "0123456789" * 5  # 50 characters
    chunks = small_chunker.split_text(text)
    
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Verify overlap between consecutive chunks
        overlap_size = (current_chunk.metadata["end_char"] - 
                       next_chunk.metadata["start_char"])
        assert overlap_size == small_chunker.chunk_overlap 