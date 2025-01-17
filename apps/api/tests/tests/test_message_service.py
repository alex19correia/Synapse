import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock

from src.models.message import Message, MessageRole
from src.services.message_service import MessageService

@pytest.fixture
def mock_db():
    """Fixture para simular a base de dados."""
    return Mock(
        table=Mock(return_value=Mock(
            insert=Mock(return_value=AsyncMock()),
            select=Mock(return_value=AsyncMock()),
            update=Mock(return_value=AsyncMock())
        ))
    )

@pytest.fixture
def message_service(mock_db):
    """Fixture para criar uma instância do MessageService."""
    return MessageService(mock_db)

@pytest.mark.asyncio
async def test_save_message(message_service, mock_db):
    """Testa a função de salvar mensagem."""
    # Arrange
    test_message = Message(
        session_id="test-session",
        role=MessageRole.USER,
        content="Test message"
    )
    mock_db.table().insert().execute.return_value.data = [test_message.model_dump()]

    # Act
    result = await message_service.save_message(test_message)

    # Assert
    assert result is not None
    assert result['content'] == "Test message"
    mock_db.table().insert().execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_session_messages(message_service, mock_db):
    """Testa a função de obter mensagens de uma sessão."""
    # Arrange
    test_messages = [
        {
            'session_id': 'test-session',
            'role': 'user',
            'content': 'Message 1',
            'timestamp': datetime.now(UTC)
        }
    ]
    
    # Configurar o mock corretamente
    mock_response = AsyncMock()
    mock_response.data = test_messages
    
    mock_db.table.return_value.select.return_value.execute = AsyncMock(
        return_value=mock_response
    )

    # Act
    messages = await message_service.get_session_messages('test-session')

    # Assert
    assert len(messages) == 1
    assert messages[0].content == 'Message 1' 