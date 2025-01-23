"""Unit tests for settings module."""
import pytest
from src.config.settings import Settings, get_settings
from src.config.test_settings import TestSettings

def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.app_name == "Synapse API"
    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.redis_url == "redis://localhost:6379"
    assert settings.model_name == "deepseek"

def test_settings_override():
    """Test settings override via environment variables."""
    settings = Settings(
        app_name="Test API",
        environment="test",
        debug=False
    )
    assert settings.app_name == "Test API"
    assert settings.environment == "test"
    assert settings.debug is False

def test_test_settings():
    """Test test settings configuration."""
    settings = TestSettings()
    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.test_redis_url == "redis://localhost:6379/1"
    assert settings.test_timeout == 5.0

def test_get_settings():
    """Test get_settings function."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_name == "Synapse API" 