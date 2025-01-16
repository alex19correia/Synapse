"""Tests for the LLM service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import ValidationError
from src.services.llm_service import LLMService, DeepSeekClient
from src.config.llm_config import LLMConfig
from src.core.cache import CacheService
from loguru import logger
import logging
import sys

class MockStreamResponse:
    """Mock response for streaming."""
    def __init__(self, chunks):
        self.chunks = chunks
        self.index = 0
        
    def __aiter__(self):
        return self
        
    async def __anext__(self):
        if self.index >= len(self.chunks):
            raise StopAsyncIteration
        chunk = self.chunks[self.index]
        self.index += 1
        return chunk

@pytest.fixture
def mock_deepseek():
    """Mock DeepSeek client."""
    mock = AsyncMock()
    mock.generate.return_value = "Test response"
    
    async def mock_stream(*args, **kwargs):
        async def inner():
            yield "Test"
            yield " response"
        return inner()
    
    mock.generate_stream = AsyncMock(side_effect=mock_stream)
    return mock

@pytest.fixture
def mock_cache():
    """Fixture for mocked cache service."""
    mock = AsyncMock(spec=CacheService)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    return mock

@pytest.fixture
def config():
    """Fixture for LLM config."""
    return LLMConfig(
        provider="test",
        model_name="test-model",
        api_key="test-key",
        temperature=0.7,
        max_tokens=100,
        cache_ttl=3600
    )

@pytest.fixture
def llm_service(mock_cache, mock_deepseek, config):
    """Fixture for LLM service."""
    service = LLMService(mock_cache, config)
    service.client = mock_deepseek
    return service

@pytest.fixture
def setup_loguru(caplog):
    """Configure loguru to work with pytest's caplog."""
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler = PropagateHandler()
    handler_id = logger.add(handler, format="{message}")
    caplog.set_level(logging.DEBUG)

    yield

    logger.remove(handler_id)

@pytest.mark.asyncio
async def test_initialization(mock_cache, mock_deepseek, config):
    """Test service initialization."""
    service = LLMService(mock_cache, config)
    assert service.cache == mock_cache
    assert service.config == config

@pytest.mark.asyncio
async def test_get_completion_basic(llm_service):
    """Test basic completion."""
    prompt = "Test prompt"
    response = await llm_service.get_completion(prompt)
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_with_context(llm_service):
    """Test completion with context."""
    prompt = "Test prompt"
    context = {"key": "value"}
    response = await llm_service.get_completion(prompt, context)
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_empty_prompt(llm_service):
    """Test empty prompt handling."""
    with pytest.raises(ValueError):
        await llm_service.get_completion("")

@pytest.mark.asyncio
async def test_get_completion_from_cache(llm_service):
    """Test completion from cache."""
    llm_service.cache.get.return_value = "Cached response"
    response = await llm_service.get_completion("Test prompt")
    assert response == "Cached response"
    llm_service.client.generate.assert_not_called()

@pytest.mark.asyncio
async def test_get_completion_cache_miss(llm_service):
    """Test cache miss."""
    llm_service.cache.get.return_value = None
    response = await llm_service.get_completion("Test prompt")
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_cache_error(llm_service):
    """Test cache error handling."""
    llm_service.cache.get.side_effect = Exception("Cache error")
    response = await llm_service.get_completion("Test prompt")
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_cache_save_error(llm_service):
    """Test cache save error handling."""
    llm_service.cache.set.side_effect = Exception("Cache save error")
    response = await llm_service.get_completion("Test prompt")
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_with_config_params(llm_service):
    """Test completion with config parameters."""
    response = await llm_service.get_completion("Test prompt")
    assert response == "Test response"
    llm_service.client.generate.assert_called_once_with(
        prompt="User: Test prompt\nAssistant: ",
        temperature=0.7,
        max_tokens=100
    )

@pytest.mark.asyncio
async def test_get_completion_with_deepseek(llm_service):
    """Test completion using DeepSeek client."""
    response = await llm_service.get_completion("Test prompt")
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_streaming(llm_service):
    """Test streaming completion."""
    prompt = "Test prompt"
    
    chunks = []
    async for chunk in llm_service.get_completion_stream(prompt):
        chunks.append(chunk)
    
    assert chunks == ["Test", " response"]
    llm_service.client.generate_stream.assert_called_once_with(
        prompt="User: Test prompt\nAssistant: ",
        temperature=0.7,
        max_tokens=100
    )

@pytest.mark.asyncio
async def test_get_completion_provider_error(llm_service):
    """Test provider error handling."""
    llm_service.client.generate.side_effect = Exception("API error")
    with pytest.raises(Exception, match="Erro ao gerar resposta do modelo"):
        await llm_service.get_completion("Test prompt")

@pytest.mark.asyncio
async def test_get_completion_with_system_prompt(llm_service):
    """Test completion with system prompt."""
    prompt = "Test prompt"
    context = {"system_prompt": "You are a helpful assistant"}
    response = await llm_service.get_completion(prompt, context)
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_with_history(llm_service):
    """Test completion with conversation history."""
    prompt = "Test prompt"
    context = {
        "history": [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"}
        ]
    }
    response = await llm_service.get_completion(prompt, context)
    assert response == "Test response"
    llm_service.client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_config_values():
    """Test invalid config values."""
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        LLMConfig(
            provider="test",
            model_name="test-model",
            api_key="test-key",
            temperature=2.0,  # Invalid temperature
            max_tokens=100,
            cache_ttl=3600
        ) 

@pytest.mark.asyncio
async def test_logging_initialization(mock_cache, config, caplog, setup_loguru):
    """Test logging during service initialization."""
    service = LLMService(mock_cache, config)
    assert "🔧 LLMService inicializado com:" in caplog.text
    assert str(mock_cache) in caplog.text
    assert "config=LLMConfig" in caplog.text
    assert "provider='test'" in caplog.text
    assert "model_name='test-model'" in caplog.text

@pytest.mark.asyncio
async def test_logging_completion(llm_service, caplog, setup_loguru):
    """Test logging during completion generation."""
    await llm_service.get_completion("Test prompt")
    assert "📨 Gerando resposta para prompt: Test prompt" in caplog.text
    assert "🔍 Contexto: None" in caplog.text
    assert "✅ Resposta gerada: Test response" in caplog.text

@pytest.mark.asyncio
async def test_logging_completion_error(llm_service, caplog, setup_loguru):
    """Test logging during completion error."""
    llm_service.client.generate.side_effect = Exception("API error")
    with pytest.raises(Exception):
        await llm_service.get_completion("Test prompt")
    assert "❌ Erro ao gerar resposta do modelo" in caplog.text
    assert "API error" in caplog.text

@pytest.mark.asyncio
async def test_logging_streaming(llm_service, caplog, setup_loguru):
    """Test logging during streaming completion."""
    chunks = []
    async for chunk in llm_service.get_completion_stream("Test prompt"):
        chunks.append(chunk)
    assert "📨 Gerando resposta em streaming para prompt: Test prompt" in caplog.text
    assert "🔍 Contexto: None" in caplog.text

@pytest.mark.asyncio
async def test_logging_streaming_error(llm_service, caplog, setup_loguru):
    """Test logging during streaming error."""
    llm_service.client.generate_stream.side_effect = Exception("Stream error")
    with pytest.raises(Exception):
        async for _ in llm_service.get_completion_stream("Test prompt"):
            pass
    assert "❌ Erro ao gerar resposta em streaming" in caplog.text
    assert "Stream error" in caplog.text

@pytest.mark.asyncio
async def test_logging_cache_operations(llm_service, caplog, setup_loguru):
    """Test logging during cache operations."""
    llm_service.cache.get.return_value = "Cached response"
    await llm_service.get_completion("Test prompt")
    assert "🔑 Verificando cache" in caplog.text
    assert "✨ Usando resposta do cache" in caplog.text

@pytest.mark.asyncio
async def test_logging_cache_error(llm_service, caplog, setup_loguru):
    """Test logging during cache error."""
    llm_service.cache.get.side_effect = Exception("Cache error")
    await llm_service.get_completion("Test prompt")
    assert "⚠️ Erro ao acessar cache" in caplog.text
    assert "Cache error" in caplog.text 