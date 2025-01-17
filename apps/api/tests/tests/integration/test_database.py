import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os
from typing import Dict, Any

from src.database import Database

# Test data
TEST_USER_DATA = {
    "email": "test@example.com",
    "name": "Test User"
}

TEST_SESSION_DATA = {
    "user_id": "test-user-id",
    "title": "Test Session"
}

TEST_MESSAGE_DATA = {
    "session_id": "test-session-id",
    "role": "user",
    "content": "Test message"
}

class MockSupabaseResponse:
    """Mock for Supabase response."""
    def __init__(self, data):
        self.data = data

class MockSupabaseQuery:
    """Mock for Supabase query builder."""
    def __init__(self, return_data=None):
        self.return_data = return_data
        
    def eq(self, *args, **kwargs):
        return self
        
    def order(self, *args, **kwargs):
        return self
        
    def limit(self, *args, **kwargs):
        return self
        
    def execute(self):
        return MockSupabaseResponse(self.return_data)

class MockSupabaseTable:
    """Mock for Supabase table operations."""
    def __init__(self, return_data=None):
        self.return_data = return_data
        
    def select(self, *args, **kwargs):
        return MockSupabaseQuery(self.return_data)
        
    def insert(self, *args, **kwargs):
        return MockSupabaseQuery(self.return_data)

@pytest.fixture
async def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("src.database.create_client") as mock_create:
        mock_client = AsyncMock()
        mock_client.table = MagicMock(return_value=MockSupabaseTable())
        mock_create.return_value = mock_client
        yield mock_client

@pytest.fixture
async def db(mock_supabase):
    """Database instance with mocked Supabase client."""
    database = Database(auto_connect=True)
    return database

@pytest.mark.asyncio
class TestDatabaseIntegration:
    """Test suite for database integration."""
    
    async def test_connection(self, db, mock_supabase):
        """Test database connection."""
        assert db.client is not None
        
    async def test_create_user_success(self, db, mock_supabase):
        """Test successful user creation."""
        # Setup mock response
        mock_supabase.table.return_value = MockSupabaseTable([TEST_USER_DATA])
        
        # Test
        result = await db.create_user(TEST_USER_DATA)
        
        # Verify
        assert result == TEST_USER_DATA
        mock_supabase.table.assert_called_with('users')
        
    async def test_create_user_failure(self, db, mock_supabase):
        """Test user creation failure."""
        # Setup mock to return no data
        mock_supabase.table.return_value = MockSupabaseTable(None)
        
        # Test
        result = await db.create_user(TEST_USER_DATA)
        
        # Verify
        assert result is None
        
    async def test_get_user_by_email_found(self, db, mock_supabase):
        """Test getting user by email when user exists."""
        # Setup mock response
        mock_supabase.table.return_value = MockSupabaseTable([TEST_USER_DATA])
        
        # Test
        result = await db.get_user_by_email(TEST_USER_DATA["email"])
        
        # Verify
        assert result == TEST_USER_DATA
        mock_supabase.table.assert_called_with('users')
        
    async def test_get_user_by_email_not_found(self, db, mock_supabase):
        """Test getting user by email when user doesn't exist."""
        # Setup mock to return no data
        mock_supabase.table.return_value = MockSupabaseTable([])
        
        # Test
        result = await db.get_user_by_email("nonexistent@example.com")
        
        # Verify
        assert result is None
        
    async def test_create_chat_session_success(self, db, mock_supabase):
        """Test successful chat session creation."""
        # Setup mock response
        mock_supabase.table.return_value = MockSupabaseTable([TEST_SESSION_DATA])
        
        # Test
        result = await db.create_chat_session(TEST_SESSION_DATA["user_id"], TEST_SESSION_DATA["title"])
        
        # Verify
        assert result == TEST_SESSION_DATA
        mock_supabase.table.assert_called_with('chat_sessions')
        
    async def test_create_chat_session_with_default_title(self, db, mock_supabase):
        """Test chat session creation with default title."""
        # Setup mock response
        expected_data = {**TEST_SESSION_DATA, "title": "Nova Conversa"}
        mock_supabase.table.return_value = MockSupabaseTable([expected_data])
        
        # Test
        result = await db.create_chat_session(TEST_SESSION_DATA["user_id"])
        
        # Verify
        assert result == expected_data
        
    async def test_add_message_success(self, db, mock_supabase):
        """Test successful message addition."""
        # Setup mock response
        mock_supabase.table.return_value = MockSupabaseTable([TEST_MESSAGE_DATA])
        
        # Test
        result = await db.add_message(
            TEST_MESSAGE_DATA["session_id"],
            TEST_MESSAGE_DATA["role"],
            TEST_MESSAGE_DATA["content"]
        )
        
        # Verify
        assert result == TEST_MESSAGE_DATA
        mock_supabase.table.assert_called_with('messages')
        
    async def test_add_message_invalid_role(self, db, mock_supabase):
        """Test message addition with invalid role."""
        # Test
        result = await db.add_message(
            TEST_MESSAGE_DATA["session_id"],
            "invalid_role",
            TEST_MESSAGE_DATA["content"]
        )
        
        # Verify
        assert result is None
        
    async def test_get_chat_history_success(self, db, mock_supabase):
        """Test successful chat history retrieval."""
        # Setup mock response
        mock_messages = [TEST_MESSAGE_DATA, TEST_MESSAGE_DATA]
        mock_supabase.table.return_value = MockSupabaseTable(mock_messages)
        
        # Test
        result = await db.get_chat_history(TEST_MESSAGE_DATA["session_id"])
        
        # Verify
        assert result == mock_messages
        mock_supabase.table.assert_called_with('messages')
        
    async def test_get_chat_history_with_limit(self, db, mock_supabase):
        """Test chat history retrieval with limit."""
        # Setup mock response
        mock_messages = [TEST_MESSAGE_DATA]
        mock_supabase.table.return_value = MockSupabaseTable(mock_messages)
        
        # Test
        result = await db.get_chat_history(TEST_MESSAGE_DATA["session_id"], limit=1)
        
        # Verify
        assert result == mock_messages
        
    async def test_get_user_sessions_success(self, db, mock_supabase):
        """Test successful user sessions retrieval."""
        # Setup mock response
        mock_sessions = [TEST_SESSION_DATA, TEST_SESSION_DATA]
        mock_supabase.table.return_value = MockSupabaseTable(mock_sessions)
        
        # Test
        result = await db.get_user_sessions(TEST_SESSION_DATA["user_id"])
        
        # Verify
        assert result == mock_sessions
        mock_supabase.table.assert_called_with('chat_sessions')
        
    async def test_get_user_sessions_empty(self, db, mock_supabase):
        """Test user sessions retrieval when no sessions exist."""
        # Setup mock to return no data
        mock_supabase.table.return_value = MockSupabaseTable([])
        
        # Test
        result = await db.get_user_sessions(TEST_SESSION_DATA["user_id"])
        
        # Verify
        assert result == [] 