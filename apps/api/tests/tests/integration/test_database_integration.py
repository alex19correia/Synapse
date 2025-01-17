"""Integration tests for database functionality."""
import pytest
import os
from datetime import datetime, timedelta
from jose import jwt
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from src.database import Database
from src.config.settings import Settings
from src.api.dependencies import get_current_user

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
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
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
async def settings():
    """Fixture to get settings instance."""
    return Settings()

@pytest.fixture
async def db(mock_supabase):
    """Fixture to get database instance with mocked Supabase client."""
    with patch('src.database.create_client', return_value=mock_supabase):
        db = Database(auto_connect=True)
        yield db

@pytest.fixture
def test_user():
    """Fixture to create test user data."""
    return {
        "email": f"test_{datetime.utcnow().timestamp()}@example.com",
        "name": "Test User",
        "id": f"test-user-{datetime.utcnow().timestamp()}"
    }

@pytest.fixture
def valid_token(settings, test_user):
    """Fixture to create a valid JWT token."""
    expire = datetime.utcnow() + timedelta(minutes=15)
    claims = {
        "sub": test_user["email"],
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_authentication_flow(settings, db, test_user, valid_token, mock_supabase):
    """Test complete user authentication flow."""
    # Setup mock data
    mock_table = MockSupabaseTable([test_user])
    mock_supabase.table.return_value = mock_table
    
    # 1. Create user in database
    created_user = await db.create_user(test_user)
    assert created_user is not None
    assert created_user["email"] == test_user["email"]
    
    # 2. Verify user can be retrieved
    user = await db.get_user_by_email(test_user["email"])
    assert user is not None
    assert user["email"] == test_user["email"]
    
    # 3. Test token validation
    authenticated_user = await get_current_user(valid_token, settings, db)
    assert authenticated_user is not None
    assert authenticated_user["email"] == test_user["email"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_session_persistence(settings, db, test_user, mock_supabase):
    """Test user session creation and retrieval."""
    # Setup mock data
    mock_table = MockSupabaseTable([test_user])
    mock_supabase.table.return_value = mock_table
    
    # 1. Create user
    user = await db.create_user(test_user)
    assert user is not None
    
    # 2. Create multiple chat sessions
    session1 = await db.create_chat_session(user["id"], "Test Chat 1")
    session2 = await db.create_chat_session(user["id"], "Test Chat 2")
    
    assert session1 is not None
    assert session2 is not None
    assert "id" in session1
    assert "id" in session2
    
    # Update mock data for sessions retrieval
    sessions = [session1, session2]
    mock_table = MockSupabaseTable(sessions)
    mock_supabase.table.return_value = mock_table
    
    # 3. Verify sessions can be retrieved
    retrieved_sessions = await db.get_user_sessions(user["id"])
    assert len(retrieved_sessions) == 2
    assert any(s["title"] == "Test Chat 1" for s in retrieved_sessions)
    assert any(s["title"] == "Test Chat 2" for s in retrieved_sessions)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_history_sync(settings, db, test_user, mock_supabase):
    """Test message history synchronization."""
    # Setup mock data
    mock_table = MockSupabaseTable([test_user])
    mock_supabase.table.return_value = mock_table
    
    # 1. Create user and session
    user = await db.create_user(test_user)
    session = await db.create_chat_session(user["id"])
    assert session is not None
    assert "id" in session
    
    # 2. Add messages to session
    message1 = await db.add_message(session["id"], "user", "Hello")
    message2 = await db.add_message(session["id"], "assistant", "Hi there")
    
    assert message1 is not None
    assert message2 is not None
    assert "id" in message1
    assert "id" in message2
    
    # Update mock data for message retrieval
    messages = [message1, message2]
    mock_table = MockSupabaseTable(messages)
    mock_supabase.table.return_value = mock_table
    
    # 3. Verify message history
    history = await db.get_chat_history(session["id"])
    assert len(history) == 2
    assert history[0]["content"] == "Hello"
    assert history[1]["content"] == "Hi there"
    
    # 4. Test history with limit
    limited_history = await db.get_chat_history(session["id"], limit=1)
    assert len(limited_history) == 1 