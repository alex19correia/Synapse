"""
Tests for the API endpoints.
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from jose import jwt
import time

from src.api.router import app
from src.api.dependencies import get_settings, get_llm_client, get_current_user, get_rag_system
from src.config.settings import Settings
from src.analytics.metrics.api_metrics import APIMetrics

# Create mock settings with all required fields
mock_settings = Settings(
    REDIS_URL="redis://localhost:6379",
    SUPABASE_URL="http://test.supabase.co",
    SUPABASE_KEY="test-key",
    JWT_SECRET_KEY="test-secret",
    JWT_ALGORITHM="HS256",
    JWT_EXPIRE_MINUTES=1440,
    MODEL_NAME="test-model",
    TEMPERATURE=0.7,
    MAX_TOKENS=100,
    RATE_LIMIT_REQUESTS=100,
    RATE_LIMIT_TIME=60,
    HOST="localhost",
    PORT=8000,
    LOG_LEVEL="DEBUG",
    ENV="test"
)

# Create mock LLM client
mock_llm = AsyncMock()
mock_llm.generate.return_value = {
    "id": "test-id",
    "content": "Test response",
    "finish_reason": "stop",
    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
}

# Create mock RAG system
mock_rag = MagicMock()

# Create mock user
mock_user = MagicMock()
mock_user.username = "test_user"

# Create mock metrics
mock_metrics = MagicMock(spec=APIMetrics)
mock_metrics.track_request = AsyncMock()
mock_metrics.start_request = AsyncMock()
mock_metrics.end_request = AsyncMock()

@pytest.fixture(autouse=True)
def setup_dependencies():
    """Setup test dependencies including settings and auth override"""
    # Create test token with proper format
    token = jwt.encode(
        {
            "sub": "test_user",
            "exp": int(time.time()) + 3600,  # 1 hour expiry
            "iat": int(time.time())
        }, 
        mock_settings.JWT_SECRET_KEY, 
        algorithm=mock_settings.JWT_ALGORITHM
    )
    
    # Create mock user
    mock_user = MagicMock()
    mock_user.username = "test_user"
    
    # Override dependencies
    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_llm_client] = lambda: mock_llm
    app.dependency_overrides[get_rag_system] = lambda: mock_rag
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    # Create test client with auth header
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {token}"}
    
    # Mock APIMetrics singleton
    with patch("src.api.router.metrics", mock_metrics):
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    mock_llm.reset_mock()
    mock_metrics.reset_mock()

def test_health_check(setup_dependencies):
    """Test health check endpoint returns 200 OK"""
    client = setup_dependencies
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_completion_success(setup_dependencies):
    """Test chat completion with valid input"""
    client = setup_dependencies
    response = client.post(
        "/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "choices" in data
    assert "usage" in data
    assert data["choices"][0]["message"]["content"] == "Test response"
    
    mock_metrics.start_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    )
    mock_metrics.track_request.assert_awaited_once_with(
        endpoint="/chat/completions",
        method="POST",
        status="success",
        duration=pytest.approx(0, abs=1)
    )
    mock_metrics.end_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    )

def test_chat_completion_unauthorized():
    """Test chat completion requires authentication"""
    # Create new client without auth header
    client = TestClient(app)
    # Override settings to ensure consistent secret key
    app.dependency_overrides = {
        get_settings: lambda: mock_settings,
        get_llm_client: lambda: mock_llm,
        get_rag_system: lambda: mock_rag
    }
    response = client.post(
        "/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    # Clean up override
    app.dependency_overrides.clear()

def test_chat_completion_error(setup_dependencies):
    """Test chat completion handles errors gracefully"""
    client = setup_dependencies
    mock_llm.generate.side_effect = Exception("Test error")
    response = client.post(
        "/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        }
    )
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]
    
    mock_metrics.start_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    )
    mock_metrics.track_request.assert_awaited_once_with(
        endpoint="/chat/completions",
        method="POST",
        status="error",
        duration=pytest.approx(0, abs=1)
    )
    mock_metrics.end_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    )

def test_chat_completion_invalid_request(setup_dependencies):
    """Test chat completion with invalid request data"""
    client = setup_dependencies
    response = client.post(
        "/chat/completions",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_metrics_tracking(setup_dependencies):
    """Test metrics are tracked for requests"""
    client = setup_dependencies
    response = client.post(
        "/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        }
    )
    assert response.status_code == 200
    
    mock_metrics.start_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    )
    mock_metrics.track_request.assert_awaited_once_with(
        endpoint="/chat/completions",
        method="POST",
        status="success",
        duration=pytest.approx(0, abs=1)
    )
    mock_metrics.end_request.assert_awaited_once_with(
        method="POST",
        endpoint="/chat/completions"
    ) 