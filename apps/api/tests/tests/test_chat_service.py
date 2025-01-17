import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from src.models.message import Message, MessageRole
from src.services.chat_service import ChatService

@pytest.fixture
def mock_message_service():
    """Fixture para simular o MessageService."""
    return Mock(
        save_message=AsyncMock(),
        get_session_messages=AsyncMock()
    )

@pytest.fixture
def mock_llm_service():
    """Fixture para simular o LLMService."""
    return Mock(
        get_completion=AsyncMock(return_value="Test response"),
        current_provider="test-provider"
    )

@pytest.fixture
def chat_service(mock_message_service, mock_llm_service):
    """Fixture para criar uma instância do ChatService."""
    return ChatService(mock_message_service, mock_llm_service)

@pytest.mark.asyncio
async def test_process_message(chat_service, mock_message_service, mock_llm_service):
    """Testa o processamento completo de uma mensagem."""
    # Arrange
    session_id = "test-session"
    content = "Test message"
    mock_message_service.save_message.return_value = {
        'id': '1',
        'session_id': session_id,
        'role': 'assistant',
        'content': 'Test response',
        'metadata': {'llm_provider': 'test-provider'}
    }

    # Act
    result = await chat_service.process_message(session_id, content)

    # Assert
    assert result is not None
    assert result.content == "Test response"
    assert mock_message_service.save_message.call_count == 2
    mock_llm_service.get_completion.assert_called_once_with(content) 