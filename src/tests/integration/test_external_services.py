"""Integration tests for external services (LLM and RAG)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.config.settings import Settings
from src.llm.deepseek_client import DeepSeekClient, DeepSeekMessage, DeepSeekResponse
from src.rag.rag_system import RAGSystem, Document
from src.database import Database
from src.api.dependencies import get_settings, get_llm_client, get_rag_system

@pytest.fixture
def settings():
    """Mock settings."""
    return Settings(
        DEEPSEEK_API_KEY="test-key",
        MODEL_NAME="test-model",
        TEMPERATURE=0.7,
        MAX_TOKENS=1000,
        REDIS_URL="redis://localhost:6379",
        SUPABASE_URL="http://localhost:8000",
        SUPABASE_KEY="test-key",
        JWT_SECRET_KEY="test-secret",
        JWT_ALGORITHM="HS256"
    )

@pytest.fixture
def mock_llm():
    """Mock LLM client."""
    mock = AsyncMock(spec=DeepSeekClient)
    mock.generate.return_value = DeepSeekResponse(
        content="Test response",
        finish_reason="stop",
        usage={"prompt_tokens": 10, "completion_tokens": 20}
    )
    return mock

@pytest.fixture
def mock_rag():
    """Mock RAG system."""
    mock = AsyncMock(spec=RAGSystem)
    mock.get_context.return_value = "Test context"
    mock.index_document.return_value = "doc-123"
    return mock

async def test_llm_integration(mock_llm):
    """Test LLM service integration."""
    messages = [
        DeepSeekMessage(role="user", content="Hello!"),
        DeepSeekMessage(role="assistant", content="Hi there!")
    ]
    
    response = await mock_llm.generate(messages)
    
    assert response.content == "Test response"
    assert response.finish_reason == "stop"
    assert response.usage == {"prompt_tokens": 10, "completion_tokens": 20}
    mock_llm.generate.assert_awaited_once_with(messages)

async def test_rag_integration(mock_rag):
    """Test RAG system integration."""
    document = Document(content="Test document", metadata={"source": "test"})
    
    doc_id = await mock_rag.index_document(document)
    context = await mock_rag.get_context("test query")
    
    assert doc_id == "doc-123"
    assert context == "Test context"
    mock_rag.index_document.assert_awaited_once_with(document)
    mock_rag.get_context.assert_awaited_once_with("test query")

async def test_llm_rag_integration(mock_llm, mock_rag):
    """Test LLM and RAG system integration."""
    # Get context from RAG
    context = await mock_rag.get_context("test query")
    
    # Generate response with context
    messages = [
        DeepSeekMessage(role="system", content=f"Use this context: {context}"),
        DeepSeekMessage(role="user", content="test query")
    ]
    response = await mock_llm.generate(messages)
    
    assert context == "Test context"
    assert response.content == "Test response"
    mock_rag.get_context.assert_awaited_once_with("test query")
    mock_llm.generate.assert_awaited_once_with(messages) 