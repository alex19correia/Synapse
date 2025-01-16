"""Unit tests for the message service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

from src.models.message import Message, MessageRole
from src.services.message_service import MessageService
from src.exceptions import MessageValidationError, DatabaseError

@pytest.fixture
def mock_db():
    """Create a mock database instance."""
    mock = MagicMock()
    
    # Mock for table().insert()
    insert_mock = MagicMock()
    insert_mock.execute = AsyncMock()
    table_mock = MagicMock()
    table_mock.insert = MagicMock(return_value=insert_mock)
    
    # Mock for table().select()
    execute_mock = AsyncMock()
    order_by_mock = MagicMock()
    order_by_mock.execute = execute_mock
    order_by_mock.limit = MagicMock(return_value=order_by_mock)
    order_by_mock.offset = MagicMock(return_value=order_by_mock)
    where_mock = MagicMock()
    where_mock.order_by = MagicMock(return_value=order_by_mock)
    select_mock = MagicMock()
    select_mock.where = MagicMock(return_value=where_mock)
    table_mock.select = MagicMock(return_value=select_mock)
    
    # Mock for table().update()
    update_execute_mock = AsyncMock()
    update_where_mock = MagicMock()
    update_where_mock.execute = update_execute_mock
    update_mock = MagicMock()
    update_mock.where = MagicMock(return_value=update_where_mock)
    table_mock.update = MagicMock(return_value=update_mock)
    
    # Mock for table().delete()
    delete_execute_mock = AsyncMock()
    delete_where_mock = MagicMock()
    delete_where_mock.execute = delete_execute_mock
    delete_mock = MagicMock()
    delete_mock.where = MagicMock(return_value=delete_where_mock)
    table_mock.delete = MagicMock(return_value=delete_mock)
    
    mock.table = MagicMock(return_value=table_mock)
    return mock

@pytest.fixture
def message_service(mock_db):
    """Create a MessageService instance with a mock database."""
    return MessageService(mock_db)

@pytest.fixture
def sample_message() -> Dict[str, Any]:
    """Create a sample message for testing."""
    return {
        'session_id': 'test-session',
        'role': 'user',
        'content': 'Test message',
        'timestamp': datetime.now(timezone.utc)
    }

@pytest.mark.asyncio
async def test_save_message_success(message_service, mock_db, sample_message):
    """Test successful message saving."""
    # Arrange
    test_message = Message(**sample_message)
    mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[test_message.model_dump()]
    )

    # Act
    result = await message_service.save_message(test_message)

    # Assert
    assert result is not None
    assert result['content'] == sample_message['content']
    mock_db.table.assert_called_once()

@pytest.mark.asyncio
async def test_save_message_database_error(message_service, mock_db, sample_message):
    """Test handling of database errors during message saving."""
    # Arrange
    test_message = Message(**sample_message)
    mock_db.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        await message_service.save_message(test_message)

@pytest.mark.asyncio
async def test_get_session_messages_success(message_service, mock_db, sample_message):
    """Test successful retrieval of session messages."""
    # Arrange
    mock_db.table.return_value.select.return_value.where.return_value.order_by.return_value.execute.return_value = MagicMock(
        data=[sample_message]
    )

    # Act
    messages = await message_service.get_session_messages('test-session')

    # Assert
    assert len(messages) == 1
    assert messages[0].content == sample_message['content']
    assert messages[0].session_id == sample_message['session_id']

@pytest.mark.asyncio
async def test_get_session_messages_empty(message_service, mock_db):
    """Test retrieval of messages for an empty session."""
    # Arrange
    mock_db.table.return_value.select.return_value.where.return_value.order_by.return_value.execute.return_value = MagicMock(
        data=[]
    )

    # Act
    messages = await message_service.get_session_messages('empty-session')

    # Assert
    assert len(messages) == 0

@pytest.mark.asyncio
async def test_update_message_success(message_service, mock_db, sample_message):
    """Test successful message update."""
    # Arrange
    message_id = "test-id"
    updated_content = "Updated message"
    mock_db.table.return_value.update.return_value.where.return_value.execute.return_value = MagicMock(
        data=[{**sample_message, 'content': updated_content}]
    )

    # Act
    result = await message_service.update_message(message_id, updated_content)

    # Assert
    assert result['content'] == updated_content
    mock_db.table.assert_called_once()

@pytest.mark.asyncio
async def test_delete_message_success(message_service, mock_db):
    """Test successful message deletion."""
    # Arrange
    message_id = "test-id"
    mock_db.table.return_value.delete.return_value.where.return_value.execute.return_value = MagicMock(
        data=[{'id': message_id}]
    )

    # Act
    result = await message_service.delete_message(message_id)

    # Assert
    assert result['id'] == message_id
    mock_db.table.assert_called_once()

@pytest.mark.asyncio
async def test_get_messages_with_pagination(message_service, mock_db, sample_message):
    """Test message retrieval with pagination."""
    # Arrange
    messages = [
        {**sample_message, 'content': f'Message {i}'}
        for i in range(5)
    ]
    mock_db.table.return_value.select.return_value.where.return_value.order_by.return_value.limit.return_value.offset.return_value.execute.return_value = MagicMock(
        data=messages[1:4]
    )

    # Act
    messages = await message_service.get_session_messages(
        'test-session',
        limit=3,
        offset=1
    )

    # Assert
    assert len(messages) == 3
    mock_db.table.assert_called_once()

@pytest.mark.asyncio
async def test_validate_message_content(message_service, sample_message):
    """Test message content validation."""
    # Test empty content
    with pytest.raises(MessageValidationError):
        await message_service.save_message(Message(
            **{**sample_message, 'content': ''}
        ))

    # Test extremely long content
    with pytest.raises(MessageValidationError):
        await message_service.save_message(Message(
            **{**sample_message, 'content': 'a' * 10001}
        ))

@pytest.mark.asyncio
async def test_validate_message_role(message_service, mock_db, sample_message):
    """Test message role validation."""
    # Test invalid role
    with pytest.raises(ValueError):
        await message_service.save_message(Message(
            **{**sample_message, 'role': 'invalid_role'}
        ))

    # Test valid roles
    for role in ['user', 'assistant', 'system']:
        mock_message = {**sample_message, 'role': role}
        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[mock_message]
        )
        msg = await message_service.save_message(Message(**mock_message))
        assert msg['role'] == role 