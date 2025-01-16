from datetime import datetime, UTC
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.models.message import Message, MessageRole
from src.main import app
from src.dependencies import get_chat_service, get_message_service

@pytest.fixture
def test_client(mock_chat_service, mock_message_service):
    """Fixture para criar um cliente de teste."""
    # Configurar resposta mock
    mock_response = Message(
        id="1",
        session_id="test-session",
        role=MessageRole.ASSISTANT,
        content="Test response",
        timestamp=datetime.now(UTC),
        metadata={"provider": "test"}
    )
    
    # Configurar o mock_chat_service corretamente
    async def mock_process_message(session_id: str, content: str):
        return mock_response
    
    mock_chat_service.process_message = AsyncMock(side_effect=mock_process_message)
    
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    app.dependency_overrides[get_message_service] = lambda: mock_message_service
    
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_send_message(test_client, mock_chat_service):
    """Testa o endpoint de envio de mensagem."""
    response = test_client.post(
        "/chat/sessions/test-session/messages",
        json={"content": "Test message"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test response"
    assert data["role"] == "assistant"
    assert data["session_id"] == "test-session"

def test_get_messages(test_client, mock_message_service):
    """Testa o endpoint de obter mensagens."""
    response = test_client.get("/chat/sessions/test-session/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 