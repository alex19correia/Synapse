"""
End-to-end tests for chat functionality, testing the complete flow from API to database.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import jwt
import time
from typing import Dict, Any

from src.api.router import app
from src.database import Database
from src.api.dependencies import get_settings, get_llm_client, get_current_user, get_rag_system
from src.config.settings import Settings

# Test data
TEST_USER = {
    "email": "test@example.com",
    "name": "Test User",
    "id": "test-user-id"
}

TEST_MESSAGE = {
    "role": "user",
    "content": "Test message"
}

# Mock settings
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

@pytest.fixture
def mock_database():
    """Create a mock database instance."""
    with patch("src.database.Database") as mock_db:
        db_instance = mock_db.return_value
        # Setup mock responses
        db_instance.create_user = AsyncMock(return_value=TEST_USER)
        db_instance.get_user_by_email = AsyncMock(return_value=TEST_USER)
        db_instance.create_chat_session = AsyncMock(return_value={"id": "test-session-id", "title": "Test Chat"})
        db_instance.add_message = AsyncMock(return_value={"id": "test-message-id", **TEST_MESSAGE})
        db_instance.get_chat_history = AsyncMock(return_value=[TEST_MESSAGE])
        yield db_instance

@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "id": "test-completion-id",
        "content": "Test response",
        "finish_reason": "stop",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }
    return mock

@pytest.fixture
def test_client(mock_database, mock_llm):
    """Create a test client with all necessary mocks."""
    # Create test token
    token = jwt.encode(
        {
            "sub": TEST_USER["email"],
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        },
        mock_settings.JWT_SECRET_KEY,
        algorithm=mock_settings.JWT_ALGORITHM
    )
    
    # Override dependencies
    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_llm_client] = lambda: mock_llm
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[get_rag_system] = lambda: MagicMock()
    
    # Create and configure test client
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {token}"}
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()

@pytest.mark.asyncio
class TestChatFlowE2E:
    """End-to-end tests for the chat functionality."""
    
    async def test_complete_chat_flow(self, test_client, mock_database, mock_llm):
        """
        Test a complete chat flow:
        1. Start a new chat session
        2. Send a message
        3. Receive a response
        4. Verify chat history
        """
        # 1. Create a new chat session
        session_response = test_client.post("/chat/sessions")
        assert session_response.status_code == 200
        session_data = session_response.json()
        assert session_data["id"] == "test-session-id"
        
        # 2. Send a user message
        chat_response = test_client.post(
            "/chat/completions",
            json={
                "session_id": session_data["id"],
                "messages": [TEST_MESSAGE]
            }
        )
        assert chat_response.status_code == 200
        completion_data = chat_response.json()
        assert completion_data["choices"][0]["message"]["content"] == "Test response"
        
        # 3. Verify the message was saved
        mock_database.add_message.assert_awaited_with(
            session_data["id"],
            TEST_MESSAGE["role"],
            TEST_MESSAGE["content"]
        )
        
        # 4. Check chat history
        history_response = test_client.get(f"/chat/sessions/{session_data['id']}/messages")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data) > 0
        assert history_data[0]["content"] == TEST_MESSAGE["content"]
    
    async def test_error_handling_flow(self, test_client, mock_database, mock_llm):
        """
        Test error handling in the chat flow:
        1. Test with invalid session ID
        2. Test with LLM failure
        3. Test with database failure
        """
        # 1. Test with invalid session ID
        invalid_response = test_client.post(
            "/chat/completions",
            json={
                "session_id": "invalid-id",
                "messages": [TEST_MESSAGE]
            }
        )
        assert invalid_response.status_code == 404
        
        # 2. Test with LLM failure
        mock_llm.generate.side_effect = Exception("LLM Error")
        error_response = test_client.post(
            "/chat/completions",
            json={
                "session_id": "test-session-id",
                "messages": [TEST_MESSAGE]
            }
        )
        assert error_response.status_code == 500
        assert "LLM Error" in error_response.json()["detail"]
        
        # 3. Test with database failure
        mock_database.add_message.side_effect = Exception("Database Error")
        db_error_response = test_client.post(
            "/chat/completions",
            json={
                "session_id": "test-session-id",
                "messages": [TEST_MESSAGE]
            }
        )
        assert db_error_response.status_code == 500
        assert "Database Error" in db_error_response.json()["detail"]
    
    async def test_authentication_flow(self, mock_database):
        """
        Test authentication flow:
        1. Test without token
        2. Test with expired token
        3. Test with invalid token
        """
        # 1. Test without token
        client_no_auth = TestClient(app)
        response = client_no_auth.post("/chat/completions")
        assert response.status_code == 401
        
        # 2. Test with expired token
        expired_token = jwt.encode(
            {
                "sub": TEST_USER["email"],
                "exp": int(time.time()) - 3600,  # 1 hour ago
                "iat": int(time.time()) - 7200
            },
            mock_settings.JWT_SECRET_KEY,
            algorithm=mock_settings.JWT_ALGORITHM
        )
        client_expired = TestClient(app)
        client_expired.headers = {"Authorization": f"Bearer {expired_token}"}
        response = client_expired.post("/chat/completions")
        assert response.status_code == 401
        
        # 3. Test with invalid token
        client_invalid = TestClient(app)
        client_invalid.headers = {"Authorization": "Bearer invalid-token"}
        response = client_invalid.post("/chat/completions")
        assert response.status_code == 401 