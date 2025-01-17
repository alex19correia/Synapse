"""Configurações de teste."""
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.config.test_settings import test_settings

# Define ambiente de teste
os.environ["ENV"] = "test"

@pytest.fixture
def test_settings():
    """Configurações para testes."""
    with patch("src.config.settings.get_settings", return_value=test_settings):
        yield test_settings

@pytest.fixture
def mock_supabase():
    """Mock do cliente Supabase."""
    mock_client = MagicMock()
    
    # Mock das operações assíncronas comuns
    mock_client.table = MagicMock(return_value=mock_client)
    mock_client.select = MagicMock(return_value=mock_client)
    mock_client.insert = MagicMock(return_value=mock_client)
    mock_client.update = MagicMock(return_value=mock_client)
    mock_client.delete = MagicMock(return_value=mock_client)
    mock_client.eq = MagicMock(return_value=mock_client)
    mock_client.execute = AsyncMock(return_value=MagicMock(data=[]))
    
    with patch("supabase.create_client", return_value=mock_client):
        yield mock_client

@pytest.fixture
def mock_redis():
    """Mock do cliente Redis."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=True)
    
    with patch("redis.asyncio.Redis.from_url", return_value=mock_client):
        yield mock_client