"""Test API routes."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.main import app
from src.api.dependencies import get_settings, get_llm_client, get_rag_system, get_supabase_client
from src.config.settings import Settings
from src.api.middleware.rate_limit import RateLimitMiddleware

@pytest.fixture
def test_client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_settings():
    """Mock settings fixture."""
    return Settings(
        OPENAI_API_KEY="test_key",
        OPENAI_MODEL="test-model",
        REDIS_URL="redis://localhost",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_KEY="test-key"
    )

@pytest.fixture
def mock_llm_client():
    """Mock LLM client fixture."""
    client = AsyncMock()
    client.complete = AsyncMock(return_value={
        "response": "Test response",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    })
    client.stream = AsyncMock(return_value=AsyncMock(__aiter__=AsyncMock(
        return_value=iter(["Test ", "streaming ", "response"])
    )))
    return client

@pytest.fixture
def mock_rag_system():
    """Mock RAG system fixture."""
    system = AsyncMock()
    system.query = AsyncMock(return_value={
        "response": "Test context response",
        "context": "Test context"
    })
    return system

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client fixture."""
    client = MagicMock()
    client.table = MagicMock(return_value=client)
    client.select = MagicMock(return_value=client)
    client.execute = AsyncMock(return_value=MagicMock(data=[]))
    return client

def setup_dependencies(mock_settings, mock_llm_client, mock_rag_system, mock_supabase_client):
    """Setup API dependencies."""
    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_rag_system] = lambda: mock_rag_system
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase_client

@pytest.fixture(autouse=True)
def setup(mock_settings, mock_llm_client, mock_rag_system, mock_supabase_client):
    """Setup and cleanup."""
    setup_dependencies(mock_settings, mock_llm_client, mock_rag_system, mock_supabase_client)
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter between tests."""
    RateLimitMiddleware.reset()

class TestAPIRoutes:
    """Test API routes."""
    
    async def test_health_check(self, test_client):
        """Tests health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    async def test_generate_completion(self, test_client, mock_llm_client):
        """Tests chat completion endpoint."""
        response = test_client.post(
            "/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "test-model"
            }
        )
        assert response.status_code == 200
        assert "response" in response.json()
        mock_llm_client.complete.assert_called_once()
    
    async def test_generate_completion_invalid_input(self, test_client):
        """Tests chat completion with invalid input."""
        response = test_client.post(
            "/chat/completions",
            json={"invalid": "input"}
        )
        assert response.status_code == 422
    
    async def test_generate_completion_with_context(self, test_client, mock_rag_system, mock_llm_client):
        """Tests chat completion with RAG context."""
        response = test_client.post(
            "/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "test-model",
                "use_rag": True
            }
        )
        assert response.status_code == 200
        assert "response" in response.json()
        mock_rag_system.query.assert_called_once()
        mock_llm_client.complete.assert_called_once()
    
    async def test_rate_limiting(self, test_client):
        """Tests rate limiting middleware."""
        # Make requests up to the limit
        for _ in range(100):
            response = test_client.get("/health")
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = test_client.get("/health")
        assert response.status_code == 429
    
    async def test_error_handling(self, test_client):
        """Tests error handling middleware."""
        def failing_llm_client():
            raise Exception("Test error")
        
        app.dependency_overrides[get_llm_client] = failing_llm_client
        
        response = test_client.post(
            "/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        assert response.status_code == 500
    
    async def test_streaming_response(self, test_client, mock_llm_client):
        """Tests streaming response."""
        async def mock_stream(*args, **kwargs):
            yield {"response": "Test chunk"}
        
        mock_llm_client.stream = mock_stream
        
        with test_client.stream(
            "POST",
            "/chat/completions/stream",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "test-model"
            }
        ) as response:
            assert response.status_code == 200
            content = b"".join(chunk for chunk in response.iter_bytes())
            assert len(content) > 0