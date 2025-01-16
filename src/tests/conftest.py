"""Pytest configuration for all tests."""
import os
import pytest
from dotenv import load_dotenv
from unittest.mock import Mock, AsyncMock
from src.database import Database
from src.services.message_service import MessageService
from src.services.chat_service import ChatService
from src.services.llm_service import LLMService

def pytest_configure(config):
    """Configure pytest."""
    # Load test environment variables
    env_file = os.path.join(os.path.dirname(__file__), '../../.env.test')
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        pytest.skip(f"Test environment file not found: {env_file}", allow_module_level=True)

    # Register custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )

@pytest.fixture
def mock_database():
    """Fixture para simular a base de dados."""
    db = Mock()
    db.table = Mock(return_value=Mock(
        insert=Mock(return_value=AsyncMock()),
        select=Mock(return_value=AsyncMock()),
        update=Mock(return_value=AsyncMock())
    ))
    return db

@pytest.fixture
def mock_message_service(mock_database):
    """Fixture para MessageService."""
    return MessageService(mock_database)

@pytest.fixture
def mock_llm_service():
    """Fixture para LLMService."""
    llm = Mock()
    llm.get_completion = AsyncMock(return_value="Mock response")
    llm.current_provider = "mock-provider"
    return llm

@pytest.fixture
def mock_chat_service(mock_message_service, mock_llm_service):
    """Fixture para ChatService."""
    return ChatService(mock_message_service, mock_llm_service)

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Fixture para simular variáveis de ambiente."""
    monkeypatch.setenv("SUPABASE_URL", "http://test.url")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key") 