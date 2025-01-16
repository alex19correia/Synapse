"""Integration tests for message flow between components."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.config.settings import Settings
from src.llm.deepseek_client import DeepSeekClient, DeepSeekMessage, DeepSeekResponse
from src.rag.rag_system import RAGSystem, Document
from src.database import Database
from src.core.cache import CacheService
from src.api.schemas import ChatRequest, ChatResponse

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
def mock_db():
    """Mock database."""
    mock = AsyncMock(spec=Database)
    mock.create_chat_session.return_value = {"id": "session-123", "title": "Test Chat"}
    mock.add_message.return_value = {"id": "msg-123", "content": "Test message"}
    mock.get_chat_history.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    return mock

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
    return mock

@pytest.fixture
def mock_cache():
    """Mock cache service."""
    mock = AsyncMock(spec=CacheService)
    mock.get.return_value = None  # Simulate cache miss
    return mock

async def test_new_chat_flow(mock_db, mock_llm, mock_rag, mock_cache):
    """Test complete flow for a new chat session."""
    # Setup test data
    user_id = "user-123"
    request = ChatRequest(messages=[{"role": "user", "content": "Hello!"}])
    
    # 1. Create new chat session
    session = await mock_db.create_chat_session(user_id)
    assert session["id"] == "session-123"
    
    # 2. Get context from RAG
    context = await mock_rag.get_context(request.messages[-1].content)
    assert context == "Test context"
    
    # 3. Generate response with context
    messages = [
        DeepSeekMessage(role="system", content=f"Use this context: {context}"),
        *[DeepSeekMessage(**msg.dict()) for msg in request.messages]
    ]
    response = await mock_llm.generate(messages)
    assert response.content == "Test response"
    
    # 4. Save messages to database
    user_msg = await mock_db.add_message(
        session_id=session["id"],
        role="user",
        content=request.messages[-1].content
    )
    assert user_msg["id"] == "msg-123"
    
    assistant_msg = await mock_db.add_message(
        session_id=session["id"],
        role="assistant",
        content=response.content
    )
    assert assistant_msg["id"] == "msg-123"

async def test_existing_chat_flow(mock_db, mock_llm, mock_rag, mock_cache):
    """Test complete flow for an existing chat session."""
    # Setup test data
    session_id = "session-123"
    request = ChatRequest(messages=[{"role": "user", "content": "What's the weather?"}])
    
    # 1. Get chat history
    history = await mock_db.get_chat_history(session_id)
    assert len(history) == 2
    
    # 2. Get context from RAG
    context = await mock_rag.get_context(request.messages[-1].content)
    assert context == "Test context"
    
    # 3. Generate response with context and history
    messages = [
        DeepSeekMessage(role="system", content=f"Use this context: {context}"),
        *[DeepSeekMessage(**msg) for msg in history],
        *[DeepSeekMessage(**msg.dict()) for msg in request.messages]
    ]
    response = await mock_llm.generate(messages)
    assert response.content == "Test response"
    
    # 4. Save new messages to database
    user_msg = await mock_db.add_message(
        session_id=session_id,
        role="user",
        content=request.messages[-1].content
    )
    assert user_msg["id"] == "msg-123"
    
    assistant_msg = await mock_db.add_message(
        session_id=session_id,
        role="assistant",
        content=response.content
    )
    assert assistant_msg["id"] == "msg-123"

async def test_cached_response_flow(mock_db, mock_llm, mock_rag, mock_cache):
    """Test flow with cached response."""
    # Setup test data
    session_id = "session-123"
    request = ChatRequest(messages=[{"role": "user", "content": "Hello!"}])
    
    # Mock cached response
    mock_cache.get.return_value = {
        "content": "Cached response",
        "finish_reason": "stop",
        "usage": {"prompt_tokens": 5, "completion_tokens": 10}
    }
    
    # 1. Check cache first
    cache_key = f"chat:response:{session_id}:{request.messages[-1].content}"
    cached_data = await mock_cache.get(cache_key)
    assert cached_data is not None
    
    # 2. Use cached response
    response = DeepSeekResponse(**cached_data)
    assert response.content == "Cached response"
    
    # 3. Save messages to database
    user_msg = await mock_db.add_message(
        session_id=session_id,
        role="user",
        content=request.messages[-1].content
    )
    assert user_msg["id"] == "msg-123"
    
    assistant_msg = await mock_db.add_message(
        session_id=session_id,
        role="assistant",
        content=response.content
    )
    assert assistant_msg["id"] == "msg-123"
    
    # Verify no calls to LLM or RAG
    mock_llm.generate.assert_not_awaited()
    mock_rag.get_context.assert_not_awaited() 