"""Tests for the configuration module."""

import pytest
from unittest.mock import patch
import os
from src.config import Settings, get_settings

# Fixtures
@pytest.fixture
def mock_env():
    """Fixture to provide a clean environment for each test."""
    with patch.dict(os.environ, {}, clear=True):
        yield

@pytest.fixture
def env_vars():
    """Fixture to provide test environment variables."""
    return {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key-123",
        "OPENAI_API_KEY": "test-openai-key",
        "COHERE_API_KEY": "test-cohere-key",
        "GOOGLE_API_KEY": "test-google-key",
        "BRAVE_API_KEY": "test-brave-key",
        "LOG_LEVEL": "DEBUG",
        "HOST": "localhost",
        "PORT": "9000"
    }

# Tests
def test_default_settings(mock_env):
    """Test default settings values."""
    settings = Settings()
    assert settings.api_version == "v1"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "INFO"
    assert settings.openai_api_key is None
    assert settings.cohere_api_key is None
    assert settings.google_api_key is None
    assert settings.brave_api_key is None

def test_settings_from_env(mock_env, env_vars):
    """Test settings loaded from environment variables."""
    with patch.dict(os.environ, env_vars):
        settings = Settings()
        assert settings.supabase_url == "https://test.supabase.co"
        assert settings.supabase_key == "test-key-123"
        assert settings.openai_api_key == "test-openai-key"
        assert settings.cohere_api_key == "test-cohere-key"
        assert settings.google_api_key == "test-google-key"
        assert settings.brave_api_key == "test-brave-key"
        assert settings.log_level == "DEBUG"
        assert settings.host == "localhost"
        assert settings.port == 9000

def test_required_fields(mock_env):
    """Test that required fields raise validation error when missing."""
    with pytest.raises(ValueError) as exc_info:
        Settings()
    error = str(exc_info.value)
    assert "supabase_url" in error
    assert "supabase_key" in error

def test_settings_cache():
    """Test that get_settings caches the result."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Same instance due to caching

def test_settings_env_file(tmp_path):
    """Test loading settings from env file."""
    env_file = tmp_path / ".env"
    env_content = """
    SUPABASE_URL=https://test-file.supabase.co
    SUPABASE_KEY=test-file-key-123
    LOG_LEVEL=DEBUG
    """
    env_file.write_text(env_content)

    with patch.object(Settings.Config, "env_file", str(env_file)):
        settings = Settings()
        assert settings.supabase_url == "https://test-file.supabase.co"
        assert settings.supabase_key == "test-file-key-123"
        assert settings.log_level == "DEBUG"

def test_settings_env_override(mock_env, env_vars, tmp_path):
    """Test that environment variables override env file values."""
    env_file = tmp_path / ".env"
    env_content = """
    SUPABASE_URL=https://file.supabase.co
    SUPABASE_KEY=file-key-123
    LOG_LEVEL=INFO
    """
    env_file.write_text(env_content)

    with patch.dict(os.environ, env_vars), \
         patch.object(Settings.Config, "env_file", str(env_file)):
        settings = Settings()
        # Environment variables should take precedence
        assert settings.supabase_url == "https://test.supabase.co"
        assert settings.supabase_key == "test-key-123"
        assert settings.log_level == "DEBUG"

def test_invalid_port_value(mock_env):
    """Test validation of port number."""
    with patch.dict(os.environ, {"PORT": "invalid"}):
        with pytest.raises(ValueError) as exc_info:
            Settings()
        assert "port" in str(exc_info.value).lower()

def test_invalid_log_level(mock_env):
    """Test validation of log level."""
    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key-123",
        "LOG_LEVEL": "INVALID"
    }):
        settings = Settings()
        # Should fall back to default
        assert settings.log_level == "INFO"

def test_settings_immutability():
    """Test that settings are immutable after creation."""
    settings = Settings(
        supabase_url="https://test.supabase.co",
        supabase_key="test-key-123"
    )
    with pytest.raises(Exception):
        settings.supabase_url = "new-value" 