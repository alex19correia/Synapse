import pytest
from unittest.mock import Mock, AsyncMock
from src.services.chat_service import ChatService
from src.services.message_service import MessageService
from src.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_message_service_create():
    """Testa a criação de mensagens no MessageService."""
    # Arrange
    mock_db = Mock()
    mock_db.add_message = AsyncMock(return_value={"id": "test-id"})
    service = MessageService(mock_db)
    
    # Act
    result = await service.create_message(
        session_id="test-session",
        role="user",
        content="Test message"
    )
    
    # Assert
    assert result["id"] == "test-id"
    mock_db.add_message.assert_called_once()

@pytest.mark.asyncio
async def test_chat_service_process_message():
    """Testa o processamento de mensagens no ChatService."""
    # Arrange
    mock_message_service = Mock()
    mock_message_service.create_message = AsyncMock(return_value={"id": "test-id"})
    
    mock_llm_service = Mock()
    mock_llm_service.get_completion = AsyncMock(return_value="Test response")
    
    service = ChatService(mock_message_service, mock_llm_service)
    
    # Act
    result = await service.process_message(
        session_id="test-session",
        content="Test message"
    )
    
    # Assert
    assert result["response"] == "Test response"
    mock_message_service.create_message.assert_called()
    mock_llm_service.get_completion.assert_called_once()

@pytest.mark.asyncio
async def test_llm_service_get_completion():
    """Testa a obtenção de respostas do LLMService."""
    # Arrange
    mock_llm = Mock()
    mock_llm.get_completion = AsyncMock(return_value="Test completion")
    service = LLMService(mock_llm)
    
    # Act
    result = await service.get_completion("Test prompt")
    
    # Assert
    assert result == "Test completion"
    mock_llm.get_completion.assert_called_once_with("Test prompt") 