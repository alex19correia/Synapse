"""Tests for the settings module."""

import os
import pytest
from unittest.mock import patch
from src.config.settings import Settings, get_settings

@pytest.fixture
def clean_env():
    """Fixture to provide a clean environment for tests."""
    original_env = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def test_env_vars(clean_env):
    """Fixture to set test environment variables."""
    os.environ.update({
        "REDIS_URL": "redis://test:6379",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "MODEL_NAME": "test-model",
        "TEMPERATURE": "0.5",
        "MAX_TOKENS": "100",
        "PORT": "8080",
        "LOG_LEVEL": "INFO"
    })
    yield

def test_default_settings():
    """Test default settings values."""
    settings = Settings()
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.MODEL_NAME == "deepseek-chat"
    assert settings.TEMPERATURE == 0.7
    assert settings.MAX_TOKENS == 1000
    assert settings.PORT == 8000
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.ENV == "development"

def test_settings_from_env(clean_env, test_env_vars):
    """Test loading settings from environment variables."""
    settings = Settings()
    assert settings.REDIS_URL == "redis://test:6379"
    assert settings.SUPABASE_URL == "https://test.supabase.co"
    assert settings.SUPABASE_KEY == "test-key"
    assert settings.MODEL_NAME == "test-model"
    assert settings.TEMPERATURE == 0.5
    assert settings.MAX_TOKENS == 100
    assert settings.PORT == 8080
    assert settings.LOG_LEVEL == "INFO"

def test_env_file_loading(clean_env):
    """Test loading settings from environment file."""
    env_contents = """
REDIS_URL=redis://env-file:6379
SUPABASE_URL=https://env-file.supabase.co
SUPABASE_KEY=env-file-key
MODEL_NAME=env-file-model
"""
    
    with open(".env.test", "w") as f:
        f.write(env_contents.strip())
    
    try:
        os.environ["ENV"] = "test"
        settings = Settings()
        assert settings.REDIS_URL == "redis://env-file:6379"
        assert settings.SUPABASE_URL == "https://env-file.supabase.co"
        assert settings.SUPABASE_KEY == "env-file-key"
        assert settings.MODEL_NAME == "env-file-model"
    finally:
        if os.path.exists(".env.test"):
            os.remove(".env.test")

def test_settings_validation():
    """Test settings validation."""
    # Test invalid temperature
    with pytest.raises(ValueError, match="Temperature must be between 0 and 1"):
        Settings(TEMPERATURE=1.5)
    
    # Test invalid max tokens
    with pytest.raises(ValueError, match="MAX_TOKENS must be positive"):
        Settings(MAX_TOKENS=0)
    
    # Test invalid port
    with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
        Settings(PORT=70000)
    
    # Test invalid log level
    with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
        Settings(LOG_LEVEL="INVALID")
    
    # Test invalid environment
    with pytest.raises(ValueError, match="ENV must be one of"):
        Settings(ENV="invalid")

def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
    
    # Verify that modifying one affects the other
    settings1.MODEL_NAME = "modified-model"
    assert settings2.MODEL_NAME == "modified-model"

def test_development_vs_test_env(clean_env):
    """Test different environment configurations."""
    # Test development environment
    os.environ["ENV"] = "development"
    dev_settings = Settings()
    assert dev_settings.ENV == "development"
    assert Settings.get_env_file() == ".env"

    # Test test environment
    os.environ["ENV"] = "test"
    test_settings = Settings()
    assert test_settings.ENV == "test"
    assert Settings.get_env_file() == ".env.test" 