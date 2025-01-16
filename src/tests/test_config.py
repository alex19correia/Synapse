"""Tests for the configuration module."""
import pytest
from unittest.mock import patch
import os
from src.config.settings import Settings, get_settings
from src.config.llm_config import LLMConfig
from src.config.ollama_config import OllamaConfig

@pytest.fixture
def mock_env():
    """Fixture to provide a clean environment for testing."""
    with patch.dict(os.environ, {}, clear=True):
        yield

@pytest.fixture
def env_vars():
    """Fixture to provide test environment variables."""
    return {
        'REDIS_URL': 'redis://test:6379',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'OPENAI_API_KEY': 'test-openai-key',
        'COHERE_API_KEY': 'test-cohere-key',
        'GOOGLE_API_KEY': 'test-google-key',
        'MODEL_NAME': 'gpt-4',
        'TEMPERATURE': '0.5',
        'MAX_TOKENS': '2000',
        'HOST': 'localhost',
        'PORT': '9000',
        'LOG_LEVEL': 'DEBUG'
    }

def test_default_settings(mock_env):
    """Test that default settings are loaded correctly."""
    settings = Settings()
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.MODEL_NAME == "deepseek-chat"
    assert settings.TEMPERATURE == 0.7
    assert settings.MAX_TOKENS == 1000
    assert settings.REQUESTS_PER_SECOND == 2
    assert settings.MAX_REQUESTS_PER_DOMAIN == 100
    assert settings.COOLDOWN_PERIOD == 60

def test_settings_from_env(mock_env, env_vars):
    """Test that settings are loaded from environment variables."""
    with patch.dict(os.environ, env_vars):
        settings = Settings()
        assert settings.REDIS_URL == 'redis://test:6379'
        assert settings.SUPABASE_URL == 'https://test.supabase.co'
        assert settings.SUPABASE_KEY == 'test-key'
        assert settings.OPENAI_API_KEY == 'test-openai-key'
        assert settings.COHERE_API_KEY == 'test-cohere-key'
        assert settings.GOOGLE_API_KEY == 'test-google-key'
        assert settings.MODEL_NAME == 'gpt-4'
        assert settings.TEMPERATURE == 0.5
        assert settings.MAX_TOKENS == 2000
        assert settings.HOST == 'localhost'
        assert settings.PORT == 9000
        assert settings.LOG_LEVEL == 'DEBUG'

def test_settings_cache():
    """Test that get_settings() returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Same instance due to singleton pattern

def test_env_file_loading(mock_env, tmp_path):
    """Test loading settings from .env file."""
    env_file = tmp_path / ".env"
    env_content = """
    REDIS_URL=redis://test:6379
    SUPABASE_URL=https://test.supabase.co
    SUPABASE_KEY=test-key
    LOG_LEVEL=DEBUG
    """
    env_file.write_text(env_content)
    
    with patch.dict(os.environ, {'ENV': 'test'}):
        with patch('src.config.settings.Settings.model_config', {'env_file': str(env_file)}):
            settings = Settings()
            assert settings.REDIS_URL == 'redis://test:6379'
            assert settings.SUPABASE_URL == 'https://test.supabase.co'
            assert settings.SUPABASE_KEY == 'test-key'
            assert settings.LOG_LEVEL == 'DEBUG'

def test_llm_config():
    """Test LLM config initialization."""
    config = LLMConfig()
    assert config.provider == "mock"
    assert config.model_name == "mock-model"
    assert config.temperature == 0.7
    assert config.max_tokens == 1000
    assert config.cache_ttl == 3600

def test_ollama_config():
    """Test Ollama config initialization."""
    config = OllamaConfig()
    assert config.model_name == "codellama"
    assert config.model_type == "completion"
    assert config.temperature == 0.1
    assert config.top_k == 10
    assert config.top_p == 0.3
    assert config.repeat_penalty == 1.1
    assert config.cache_enabled is True
    assert config.cache_capacity == 2000

def test_ollama_request_params():
    """Test Ollama config request parameters."""
    config = OllamaConfig()
    params = config.get_request_params()
    assert params["model"] == "codellama"
    assert params["options"]["temperature"] == 0.1
    assert params["options"]["num_ctx"] == 2048
    assert params["options"]["num_gpu"] == 1
    assert params["options"]["num_thread"] == 4
    assert params["options"]["top_k"] == 10
    assert params["options"]["top_p"] == 0.3
    assert params["options"]["repeat_penalty"] == 1.1
    assert params["options"]["stop"] == ["</s>", "Human:", "Assistant:"] 