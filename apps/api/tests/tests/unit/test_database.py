"""Tests for the Database class."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
from datetime import datetime
from src.database import Database

# Mock JWT token for testing
TEST_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.1234567890"
TEST_URL = "https://test.supabase.co"

@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to mock environment variables."""
    monkeypatch.setenv("SUPABASE_URL", TEST_URL)
    monkeypatch.setenv("SUPABASE_KEY", TEST_JWT)

class MockSupabaseQuery:
    def __init__(self, data=None):
        self.data = data or []
        self.last_order = None
        self.last_limit = None

    def eq(self, field, value):
        filtered_data = [d for d in self.data if d.get(field) == value]
        return MockSupabaseQuery(filtered_data)

    def order(self, field, desc=False):
        self.last_order = (field, desc)
        return self

    def limit(self, n):
        self.last_limit = n
        return self

    async def execute(self):
        data = self.data
        if self.last_limit:
            data = data[:self.last_limit]
        return type('Response', (), {'data': data})()

class MockSupabaseTable:
    def __init__(self, data=None):
        self.data = data or []
        self.last_insert = None
        self.last_select = None

    def insert(self, data):
        self.last_insert = data
        return MockSupabaseQuery([data])

    def select(self, *args):
        self.last_select = args
        return MockSupabaseQuery(self.data)

    def eq(self, field, value):
        filtered_data = [d for d in self.data if d.get(field) == value]
        return MockSupabaseQuery(filtered_data)

    def order(self, field, desc=False):
        query = MockSupabaseQuery(self.data)
        return query.order(field, desc)

    def limit(self, n):
        query = MockSupabaseQuery(self.data)
        return query.limit(n)

@pytest.fixture
def mock_supabase():
    """Fixture to mock Supabase client."""
    mock = MagicMock()
    mock.table = MagicMock(return_value=MockSupabaseTable())
    return mock

@pytest.fixture
def db(mock_env):
    """Fixture to create a Database instance."""
    return Database(auto_connect=False)

@pytest.mark.asyncio
async def test_auto_connect(mock_env, mock_supabase):
    """Test that database auto-connects when initialized with auto_connect=True."""
    with patch('src.database.create_client', return_value=mock_supabase) as mock_create:
        db = Database(auto_connect=True)
        mock_create.assert_called_once_with(TEST_URL, TEST_JWT)

@pytest.mark.asyncio
async def test_manual_connect(db):
    """Test manual connection to database."""
    with patch('src.database.create_client') as mock_create:
        db._connect()
        mock_create.assert_called_once_with(TEST_URL, TEST_JWT)

@pytest.mark.asyncio
async def test_connection_error(db):
    """Test connection error handling."""
    with patch('src.database.create_client', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception, match="Connection failed"):
            db._connect()

@pytest.mark.asyncio
async def test_create_user_success(db, mock_supabase):
    """Test successful user creation."""
    db.client = mock_supabase
    user_data = {"email": "test@example.com", "name": "Test User"}
    mock_table = MockSupabaseTable([user_data])
    mock_supabase.table.return_value = mock_table
    
    result = await db.create_user(user_data)
    
    assert result == user_data
    mock_supabase.table.assert_called_with('users')

@pytest.mark.asyncio
async def test_create_user_error(db, mock_supabase):
    """Test error handling in user creation."""
    db.client = mock_supabase
    mock_supabase.table.side_effect = Exception("Database error")
    
    result = await db.create_user({"email": "test@example.com"})
    
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_email_success(db, mock_supabase):
    """Test successful user retrieval by email."""
    db.client = mock_supabase
    user_data = {"email": "test@example.com", "name": "Test User"}
    mock_table = MockSupabaseTable([user_data])
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_user_by_email("test@example.com")
    
    assert result == user_data
    mock_supabase.table.assert_called_with('users')

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db, mock_supabase):
    """Test user retrieval when user doesn't exist."""
    db.client = mock_supabase
    mock_table = MockSupabaseTable([])
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_user_by_email("nonexistent@example.com")
    
    assert result is None

@pytest.mark.asyncio
async def test_create_chat_session_success(db, mock_supabase):
    """Test successful chat session creation."""
    db.client = mock_supabase
    session_data = {
        "user_id": "test-user-id",
        "title": "Test Chat"
    }
    mock_table = MockSupabaseTable([session_data])
    mock_supabase.table.return_value = mock_table
    
    result = await db.create_chat_session(session_data["user_id"], session_data["title"])
    
    assert result == session_data
    mock_supabase.table.assert_called_with('chat_sessions')

@pytest.mark.asyncio
async def test_create_chat_session_default_title(db, mock_supabase):
    """Test chat session creation with default title."""
    db.client = mock_supabase
    user_id = "test-user-id"
    expected_data = {
        "user_id": user_id,
        "title": "Nova Conversa"
    }
    mock_table = MockSupabaseTable([expected_data])
    mock_supabase.table.return_value = mock_table
    
    result = await db.create_chat_session(user_id)
    
    assert result == expected_data
    mock_supabase.table.assert_called_with('chat_sessions')

@pytest.mark.asyncio
async def test_create_chat_session_error(db, mock_supabase):
    """Test error handling in chat session creation."""
    db.client = mock_supabase
    mock_supabase.table.side_effect = Exception("Database error")
    
    result = await db.create_chat_session("test-user-id")
    
    assert result is None

@pytest.mark.asyncio
async def test_add_message_success(db, mock_supabase):
    """Test successful message addition."""
    db.client = mock_supabase
    message_data = {
        "session_id": "test-session-id",
        "role": "user",
        "content": "Hello!"
    }
    mock_table = MockSupabaseTable([message_data])
    mock_supabase.table.return_value = mock_table
    
    result = await db.add_message(
        message_data["session_id"],
        message_data["role"],
        message_data["content"]
    )
    
    assert result == message_data
    mock_supabase.table.assert_called_with('messages')

@pytest.mark.asyncio
async def test_add_message_invalid_role(db, mock_supabase):
    """Test message addition with invalid role."""
    db.client = mock_supabase
    
    result = await db.add_message(
        "test-session-id",
        "invalid_role",
        "Hello!"
    )
    
    assert result is None

@pytest.mark.asyncio
async def test_add_message_error(db, mock_supabase):
    """Test error handling in message addition."""
    db.client = mock_supabase
    mock_supabase.table.side_effect = Exception("Database error")
    
    result = await db.add_message(
        "test-session-id",
        "user",
        "Hello!"
    )
    
    assert result is None

@pytest.mark.asyncio
async def test_get_chat_history_success(db, mock_supabase):
    """Test successful chat history retrieval."""
    db.client = mock_supabase
    messages = [
        {"id": "1", "session_id": "test-session", "role": "user", "content": "Hello"},
        {"id": "2", "session_id": "test-session", "role": "assistant", "content": "Hi"}
    ]
    mock_table = MockSupabaseTable(messages)
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_chat_history("test-session")
    
    assert result == messages
    mock_supabase.table.assert_called_with('messages')

@pytest.mark.asyncio
async def test_get_chat_history_with_limit(db, mock_supabase):
    """Test chat history retrieval with limit."""
    db.client = mock_supabase
    messages = [
        {"id": "1", "session_id": "test-session", "role": "user", "content": "Hello"}
    ]
    mock_table = MockSupabaseTable(messages)
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_chat_history("test-session", limit=1)
    
    assert result == messages
    mock_supabase.table.assert_called_with('messages')

@pytest.mark.asyncio
async def test_get_chat_history_empty(db, mock_supabase):
    """Test chat history retrieval with no messages."""
    db.client = mock_supabase
    mock_table = MockSupabaseTable([])
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_chat_history("test-session")
    
    assert result == []
    mock_supabase.table.assert_called_with('messages')

@pytest.mark.asyncio
async def test_get_user_sessions_success(db, mock_supabase):
    """Test successful user sessions retrieval."""
    db.client = mock_supabase
    sessions = [
        {"id": "1", "user_id": "test-user", "title": "Chat 1"},
        {"id": "2", "user_id": "test-user", "title": "Chat 2"}
    ]
    mock_table = MockSupabaseTable(sessions)
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_user_sessions("test-user")
    
    assert result == sessions
    mock_supabase.table.assert_called_with('chat_sessions')

@pytest.mark.asyncio
async def test_get_user_sessions_empty(db, mock_supabase):
    """Test user sessions retrieval with no sessions."""
    db.client = mock_supabase
    mock_table = MockSupabaseTable([])
    mock_supabase.table.return_value = mock_table
    
    result = await db.get_user_sessions("test-user")
    
    assert result == []
    mock_supabase.table.assert_called_with('chat_sessions') 