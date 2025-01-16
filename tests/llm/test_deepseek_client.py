import pytest
from unittest.mock import AsyncMock, patch
from src.llm.deepseek_client import DeepSeekClient, DeepSeekMessage, DeepSeekResponse, Entity
import json
import httpx
import asyncio
from src.core.cache import Cache
from unittest import mock

@pytest.fixture
def mock_cache():
    with patch("src.llm.deepseek_client.Cache") as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_httpx():
    with patch("httpx.AsyncClient") as mock:
        mock_client = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_client
        yield mock_client

@pytest.fixture
def test_settings():
    with patch("src.config.settings.get_settings") as mock:
        mock.return_value.DEEPSEEK_API_KEY = "test_key"
        mock.return_value.MODEL_NAME = "test_model"
        mock.return_value.TEMPERATURE = 0.7
        mock.return_value.MAX_TOKENS = 1000
        mock.return_value.REDIS_URL = "redis://localhost:6379/0"
        yield mock

class AsyncIterator:
    """Helper class para criar um async iterator."""
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        try:
            item = self.items[self.index]
            self.index += 1
            return item
        except IndexError:
            raise StopAsyncIteration

@pytest.mark.asyncio
async def test_generate(mock_httpx, test_settings):
    """Testa geração básica"""
    client = DeepSeekClient()
    messages = [
        DeepSeekMessage(role="user", content="Quem é você?")
    ]
    
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Resposta de teste"},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 10}
    }
    mock_httpx.post.return_value = mock_response
    
    response = await client.generate(messages)
    assert isinstance(response, DeepSeekResponse)
    assert response.content == "Resposta de teste"
    assert response.usage["total_tokens"] == 10

@pytest.mark.asyncio
async def test_stream_generate(mock_httpx, test_settings):
    """Testa geração em streaming"""
    client = DeepSeekClient()
    messages = [
        DeepSeekMessage(role="user", content="Conte até 5.")
    ]
    
    # Mock do stream
    stream_response = AsyncMock()
    stream_response.aiter_lines = AsyncMock()
    stream_response.aiter_lines.return_value = AsyncIterator([
        'data: {"choices":[{"delta":{"content":"1"}}]}',
        'data: {"choices":[{"delta":{"content":"2"}}]}',
        'data: {"choices":[{"delta":{"content":"3"}}]}'
    ])
    mock_httpx.post.return_value = stream_response
    
    tokens = []
    async for token in client.stream_generate(messages):
        tokens.append(token)
    
    assert len(tokens) == 3
    assert tokens == ["1", "2", "3"]

@pytest.mark.asyncio
async def test_generate_with_cache(mock_cache, mock_httpx, test_settings):
    # Setup client
    client = DeepSeekClient()
    
    # Setup mock for first call (cache miss)
    mock_cache.get.return_value = None
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta de teste"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 10}
    }
    mock_httpx.post.return_value = mock_response
    
    # First call - should miss cache
    response1 = await client.generate_with_cache([DeepSeekMessage(role="user", content="Teste")])

    assert response1.content == "Resposta de teste"
    assert not response1.cached
    
    # Setup mock for second call (cache hit)
    cached_data = {
        "content": "Resposta em cache",
        "finish_reason": "stop",
        "usage": {"total_tokens": 10},
        "cached": True
    }
    mock_cache.get.return_value = cached_data
    mock_cache.ttl.return_value = 3000  # 50 minutes left
    
    # Reset HTTP mock to ensure it's not used
    mock_httpx.post.reset_mock()
    
    # Second call - should hit cache
    response2 = await client.generate_with_cache([DeepSeekMessage(role="user", content="Teste")])

    assert response2.content == "Resposta em cache"
    assert response2.cached
    mock_httpx.post.assert_not_called()

@pytest.mark.asyncio
async def test_generate_with_retry(mock_httpx, test_settings):
    """Testa geração com retry"""
    client = DeepSeekClient()
    messages = [
        DeepSeekMessage(role="user", content="Teste retry")
    ]
    
    # Simula erro nas primeiras tentativas
    error_response = AsyncMock()
    error_response.raise_for_status.side_effect = Exception("Erro")
    
    success_response = AsyncMock()
    success_response.json.return_value = {
        "choices": [{
            "message": {"content": "Sucesso após retry"},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 15}
    }
    
    mock_httpx.post.side_effect = [
        error_response,
        error_response,
        success_response
    ]
    
    response = await client.generate_with_retry(messages)
    assert isinstance(response, DeepSeekResponse)
    assert response.content == "Sucesso após retry"

@pytest.mark.asyncio
async def test_summarize(mock_httpx, test_settings):
    """Testa geração de resumo"""
    client = DeepSeekClient()
    text = """
    Python é uma linguagem de programação de alto nível, interpretada, 
    de script, imperativa, orientada a objetos, funcional, de tipagem dinâmica e forte.
    Foi lançada por Guido van Rossum em 1991.
    """
    
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Python: linguagem de alto nível criada em 1991."},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 12}
    }
    mock_httpx.post.return_value = mock_response
    
    summary = await client.summarize(text, max_length=100)
    assert isinstance(summary, str)
    assert summary == "Python: linguagem de alto nível criada em 1991."

@pytest.mark.asyncio
async def test_extract_entities(mock_httpx, test_settings):
    """Testa extração de entidades"""
    client = DeepSeekClient()
    text = "Guido van Rossum criou Python em 1991."
    
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": '''[
                    {"text": "Guido van Rossum", "type": "PERSON", "start": 0, "end": 15},
                    {"text": "Python", "type": "LANGUAGE", "start": 21, "end": 27},
                    {"text": "1991", "type": "DATE", "start": 31, "end": 35}
                ]'''
            },
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 20}
    }
    mock_httpx.post.return_value = mock_response
    
    entities = await client.extract_entities(text)
    assert isinstance(entities, list)
    assert len(entities) == 3
    assert all(isinstance(e, Entity) for e in entities)
    
    assert entities[0].text == "Guido van Rossum"
    assert entities[0].type == "PERSON"
    assert entities[1].text == "Python"
    assert entities[1].type == "LANGUAGE"
    assert entities[2].text == "1991"
    assert entities[2].type == "DATE" 

@pytest.mark.asyncio
async def test_generate_with_all_parameters(mock_httpx, test_settings):
    """Tests generate with all optional parameters."""
    client = DeepSeekClient()
    messages = [
        DeepSeekMessage(role="user", content="Test", name="tester")
    ]
    
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Test response"},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 10}
    }
    mock_httpx.post.return_value = mock_response
    
    response = await client.generate(
        messages,
        temperature=0.7,
        max_tokens=100,
        top_p=0.9,
        presence_penalty=0.1,
        frequency_penalty=0.1,
        stop=["END"]
    )
    
    # Verify the request was made with all parameters
    called_json = mock_httpx.post.call_args.kwargs["json"]
    assert called_json["temperature"] == 0.7
    assert called_json["max_tokens"] == 100
    assert called_json["top_p"] == 0.9
    assert called_json["presence_penalty"] == 0.1
    assert called_json["frequency_penalty"] == 0.1
    assert called_json["stop"] == ["END"]
    assert called_json["messages"][0]["name"] == "tester"

@pytest.mark.asyncio
async def test_cache_expiration(mock_cache, mock_httpx, test_settings):
    """Tests that cache entries expire correctly."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test cache expiration")]
    
    # First call - cache miss
    mock_cache.get.return_value = None
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 5}
    }
    mock_httpx.post.return_value = mock_response
    
    await client.generate_with_cache(messages)
    
    # Verify cache was set with expiration
    cache_key = client._get_cache_key(messages)
    mock_cache.set.assert_called_once()
    assert mock_cache.set.call_args.kwargs["ttl"] == 3600  # TTL of 1 hour

@pytest.mark.asyncio
async def test_metrics_tracking(mock_httpx, mock_cache, test_settings):
    """Tests that metrics are properly tracked."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test metrics")]

    # Mock metrics
    client.metrics = AsyncMock()
    client.metrics.start_request = AsyncMock()
    client.metrics.end_request = AsyncMock()
    client.metrics.track_request = AsyncMock()
    client.metrics.track_cache_operation = AsyncMock()

    # Mock cache miss
    mock_cache.get.return_value = None
    mock_cache.ttl.return_value = None

    # Mock API response
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 5}
    }
    mock_httpx.post.return_value = mock_response

    await client.generate_with_cache(messages)

    # Verify metrics were tracked
    assert client.metrics.start_request.called
    assert client.metrics.end_request.called
    assert client.metrics.track_cache_operation.called
    assert client.metrics.track_request.called

    # Verify cache miss was tracked
    client.metrics.track_cache_operation.assert_called_with("generate", hit=False)

    # Verify request was tracked as successful
    client.metrics.track_request.assert_called_with(
        operation="generate",
        status="success",
        latency=mock.ANY  # Time will vary
    )

@pytest.mark.asyncio
async def test_error_handling_and_retry(mock_httpx, test_settings):
    """Tests error handling and retry logic."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test errors")]
    
    # Mock a series of failures followed by success
    error_response = AsyncMock()
    error_response.raise_for_status.side_effect = httpx.HTTPError("API Error")
    
    success_response = AsyncMock()
    success_response.json.return_value = {
        "choices": [{"message": {"content": "Success"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 5}
    }
    
    # First two calls fail, third succeeds
    mock_httpx.post.side_effect = [
        error_response,
        error_response,
        success_response
    ]
    
    # Should succeed after retries
    response = await client.generate_with_retry(messages, max_retries=3)
    assert response.content == "Success"
    assert mock_httpx.post.call_count == 3

@pytest.mark.asyncio
async def test_invalid_entity_response(mock_httpx, test_settings):
    """Tests handling of invalid entity extraction response."""
    client = DeepSeekClient()
    
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Invalid JSON"},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 5}
    }
    mock_httpx.post.return_value = mock_response
    
    with pytest.raises(json.JSONDecodeError):
        await client.extract_entities("Test text") 

@pytest.mark.asyncio
async def test_cache_key_generation(mock_cache, test_settings):
    """Tests cache key generation with different message combinations."""
    client = DeepSeekClient()
    
    # Test different message combinations
    test_cases = [
        # Single message
        [DeepSeekMessage(role="user", content="Test")],
        # Multiple messages
        [
            DeepSeekMessage(role="system", content="You are a helpful assistant"),
            DeepSeekMessage(role="user", content="Test")
        ],
        # Messages with names
        [DeepSeekMessage(role="user", content="Test", name="tester")],
        # Empty content
        [DeepSeekMessage(role="user", content="")],
        # Special characters
        [DeepSeekMessage(role="user", content="Test!@#$%^&*()")]
    ]
    
    # Ensure different message combinations generate different keys
    keys = set()
    for messages in test_cases:
        key = client._get_cache_key(messages)
        keys.add(key)
    
    # Verify each combination generated a unique key
    assert len(keys) == len(test_cases)

@pytest.mark.asyncio
async def test_cache_with_invalid_data(mock_cache, mock_httpx, test_settings):
    """Tests cache behavior with invalid/corrupted cached data."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test")]
    
    # Test cases for invalid cache data
    invalid_cache_data = [
        None,  # No data
        {},  # Empty dict
        {"missing": "fields"},  # Missing required fields
        {"content": None, "finish_reason": None, "usage": None, "cached": True}  # null fields
    ]
    
    for cache_data in invalid_cache_data:
        # Setup cache with invalid data
        mock_cache.get.return_value = cache_data
        
        # Setup fallback response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Fallback response"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 5}
        }
        mock_httpx.post.return_value = mock_response
        
        # Should fallback to API call
        response = await client.generate_with_cache(messages)
        assert response.content == "Fallback response"
        assert not response.cached

@pytest.mark.asyncio
async def test_cache_race_condition(mock_cache, mock_httpx, test_settings):
    """Tests cache behavior under simulated race conditions."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test")]
    
    # Simulate cache miss followed by a delayed set
    mock_cache.get.return_value = None
    mock_cache.ttl.return_value = 3000  # 50 minutes left
    
    # Make set operation delay
    original_set = mock_cache.set
    set_called = False
    
    async def delayed_set(*args, **kwargs):
        nonlocal set_called
        set_called = True
        # Simulate another process setting the cache
        mock_cache.get.return_value = {
            "content": "Cached by another process",
            "finish_reason": "stop",
            "usage": {"total_tokens": 5},
            "cached": True
        }
        return await original_set(*args, **kwargs)
    
    mock_cache.set = delayed_set
    
    # Setup API response
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "API response"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 5}
    }
    mock_httpx.post.return_value = mock_response
    
    # Make concurrent requests
    responses = await asyncio.gather(
        client.generate_with_cache(messages),
        client.generate_with_cache(messages)
    )
    
    # Verify responses
    assert set_called
    assert any(r.content == "API response" for r in responses)
    assert any(r.content == "Cached by another process" for r in responses)

@pytest.mark.asyncio
async def test_cache_ttl_behavior(mock_cache, mock_httpx, test_settings):
    """Tests cache TTL behavior and expiration."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test TTL")]
    
    # First call - cache miss
    mock_cache.get.return_value = None
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}],
        "usage": {"total_tokens": 5}
    }
    mock_httpx.post.return_value = mock_response
    
    await client.generate_with_cache(messages)
    
    # Verify TTL was set
    cache_key = client._get_cache_key(messages)
    mock_cache.set.assert_called_once()
    assert mock_cache.set.call_args.kwargs["ttl"] == 3600  # TTL of 1 hour
    
    # Simulate near-expiration (1 second left)
    mock_cache.ttl.return_value = 1
    
    # Setup cache hit with near-expired data
    cached_data = {
        "content": "Cached response",
        "finish_reason": "stop",
        "usage": {"total_tokens": 5},
        "cached": True
    }
    mock_cache.get.return_value = cached_data
    
    # Get response when cache is about to expire
    response = await client.generate_with_cache(messages)
    assert not response.cached  # Should not use cache when TTL is too low
    assert response.content == "Response"  # Should get fresh response
    
    # Verify TTL was checked
    mock_cache.ttl.assert_called_with(cache_key)

@pytest.mark.asyncio
async def test_cache_with_different_parameters(mock_cache, mock_httpx, test_settings):
    """Tests cache behavior with different generation parameters."""
    client = DeepSeekClient()
    messages = [DeepSeekMessage(role="user", content="Test")]
    
    # Test different parameter combinations
    param_combinations = [
        {"temperature": 0.7},
        {"max_tokens": 100},
        {"top_p": 0.9},
        {"presence_penalty": 0.1},
        {"frequency_penalty": 0.1},
        {"stop": ["END"]},
        # Combined parameters
        {
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 0.9
        }
    ]
    
    for params in param_combinations:
        # Reset mocks
        mock_cache.get.return_value = None
        mock_httpx.post.reset_mock()
        
        # Setup API response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 5}
        }
        mock_httpx.post.return_value = mock_response
        
        # Generate with parameters
        await client.generate_with_cache(messages, **params)
        
        # Verify cache key includes parameters
        cache_key = mock_cache.set.call_args[0][0]  # Get the cache key used
        for param, value in params.items():
            assert f"{param}={value}" in cache_key 