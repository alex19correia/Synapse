"""Integration tests for API endpoints."""

import pytest
import jwt
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.api.router import app
from src.config.settings import Settings
from src.services.cache_service import CacheService
from src.llm.deepseek_client import DeepSeekMessage
from src.api.dependencies import (
    get_settings,
    get_database,
    get_llm_client,
    get_rag_system,
    get_cache
)

TEST_USER = {
    "id": "test-user-id",
    "email": "test@example.com",
    "name": "Test User"
}

@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limit state before each test."""
    from src.api.router import request_counts
    request_counts.clear()

@pytest.fixture
def mock_db():
    """Mock database fixture.
    
    Returns:
        AsyncMock: Mocked database instance with configured methods.
    """
    with patch("src.api.dependencies.get_database") as mock:
        db = AsyncMock()
        mock.return_value = db
        
        # Mock Supabase client
        db.client = AsyncMock()
        
        # Configure async method returns
        async def mock_get_user(*args, **kwargs):
            return TEST_USER
            
        async def mock_get_history(*args, **kwargs):
            return []
            
        # Mock table operations
        mock_table = AsyncMock()
        mock_table.select.return_value.eq.return_value.execute.return_value.data = [TEST_USER]
        db.client.table.return_value = mock_table
        
        db.get_chat_history = mock_get_history
        db.get_user_by_email = mock_get_user
        yield db

@pytest.fixture
def mock_supabase():
    """Mock Supabase client fixture.
    
    Returns:
        AsyncMock: Mocked Supabase client with configured methods.
    """
    with patch("src.database.create_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        
        # Mock table operations
        mock_table = AsyncMock()
        mock_table.select.return_value.eq.return_value.execute.return_value.data = [TEST_USER]
        client.table.return_value = mock_table
        
        # Configure auth methods
        client.auth.get_user.return_value = {"user": TEST_USER}
        
        yield client

@pytest.fixture
def test_client(settings, mock_db, mock_llm, mock_rag, mock_cache, mock_supabase):
    """Test client fixture with mocked dependencies.
    
    Args:
        settings: Application settings.
        mock_db: Mocked database instance.
        mock_llm: Mocked LLM client.
        mock_rag: Mocked RAG system.
        mock_cache: Mocked cache service.
        mock_supabase: Mocked Supabase client.
        
    Returns:
        TestClient: Configured FastAPI test client.
    """
    # Create a valid token for test user
    token = jwt.encode(
        {
            "sub": TEST_USER["email"],
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Override all dependencies
    app.dependency_overrides = {
        get_settings: lambda: settings,
        get_database: lambda: mock_db,
        get_llm_client: lambda: mock_llm,
        get_rag_system: lambda: mock_rag,
        get_cache: lambda: mock_cache
    }
    
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {token}"}
    
    yield client
    
    # Clean up
    app.dependency_overrides = {}

def test_health_check(test_client: TestClient):
    """Test health check endpoint.
    
    Args:
        test_client: FastAPI test client instance.
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_completion_success(
    test_client: TestClient,
    mock_llm: AsyncMock,
    mock_rag: AsyncMock,
    mock_db: AsyncMock,
    mock_cache: AsyncMock
):
    """Test successful chat completion.
    
    Args:
        test_client: FastAPI test client instance.
        mock_llm: Mocked LLM client.
        mock_rag: Mocked RAG system.
        mock_db: Mocked database instance.
        mock_cache: Mocked cache service.
    """
    response = test_client.post("/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 100
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-completion-id"
    assert data["choices"][0]["message"]["content"] == "Test response content"
    assert data["choices"][0]["finish_reason"] == "stop"
    assert data["usage"] == {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }

def test_chat_completion_with_history(
    test_client: TestClient,
    mock_llm: AsyncMock,
    mock_rag: AsyncMock,
    mock_db: AsyncMock,
    mock_cache: AsyncMock
):
    """Test chat completion with history.
    
    Args:
        test_client: FastAPI test client instance.
        mock_llm: Mocked LLM client.
        mock_rag: Mocked RAG system.
        mock_db: Mocked database instance.
        mock_cache: Mocked cache service.
    """
    # Setup mock history
    async def mock_get_history(session_id):
        return [{"role": "user", "content": "Previous message"}]
    mock_db.get_chat_history = mock_get_history
    
    response = test_client.post("/chat/completions", json={
        "messages": [{"role": "user", "content": "Follow-up"}],
        "session_id": "test-session"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-completion-id"
    assert data["choices"][0]["message"]["content"] == "Test response content"

def test_chat_completion_cached(
    test_client: TestClient,
    mock_llm: AsyncMock,
    mock_rag: AsyncMock,
    mock_db: AsyncMock,
    mock_cache: AsyncMock
):
    """Test chat completion with cached response.
    
    Args:
        test_client: FastAPI test client instance.
        mock_llm: Mocked LLM client.
        mock_rag: Mocked RAG system.
        mock_db: Mocked database instance.
        mock_cache: Mocked cache service.
    """
    # Setup mock cache
    async def mock_get(*args, **kwargs):
        return {
            "id": "test-completion-id",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Test response content"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
    mock_cache.get = mock_get
    
    response = test_client.post("/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-completion-id"
    assert data["choices"][0]["message"]["content"] == "Test response content"

def test_chat_completion_unauthorized(test_client: TestClient):
    """Test chat completion with invalid token.
    
    Args:
        test_client: FastAPI test client instance.
    """
    test_client.headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.post("/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 401
    assert "detail" in response.json()

def test_chat_completion_invalid_request(test_client: TestClient):
    """Test chat completion with invalid request.
    
    Args:
        test_client: FastAPI test client instance.
    """
    response = test_client.post("/chat/completions", json={
        "temperature": 0.7  # Missing required messages field
    })
    assert response.status_code == 422
    assert "detail" in response.json() 

def test_chat_completion_rate_limited(test_client: TestClient):
    """Test chat completion rate limiting.
    
    Args:
        test_client: FastAPI test client instance.
    """
    settings = get_settings()
    
    # Make requests up to the limit
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        response = test_client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        assert response.status_code == 200
        
    # This request should be rate limited
    response = test_client.post(
        "/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}]}
    )
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded. Please try again later." 