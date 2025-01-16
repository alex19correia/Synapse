import pytest
import asyncio
from src.llm.deepseek_client import DeepSeekClient, DeepSeekMessage, DeepSeekResponse
from src.config.settings import get_settings

@pytest.mark.integration
@pytest.mark.asyncio
class TestDeepSeekIntegration:
    async def test_basic_chat_completion(self):
        """Tests basic chat completion with the DeepSeek API."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="system", content="You are a helpful assistant."),
            DeepSeekMessage(role="user", content="What is 2+2?")
        ]

        response = await client.generate(messages)
        assert isinstance(response, DeepSeekResponse)
        assert response.content is not None
        assert "4" in response.content.lower()
        assert response.usage is not None
        assert response.usage["total_tokens"] > 0

    async def test_streaming_completion(self):
        """Tests streaming completion with the DeepSeek API."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="user", content="Count from 1 to 3.")
        ]

        tokens = []
        async for token in client.stream_generate(messages):
            tokens.append(token)

        # Verify we got a coherent response
        full_response = "".join(tokens)
        assert any(str(i) in full_response for i in range(1, 4))
        assert len(tokens) > 0

    async def test_concurrent_requests(self):
        """Tests handling multiple concurrent requests."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="user", content="Hello!")
        ]

        # Make 3 concurrent requests
        tasks = [
            client.generate(messages),
            client.generate(messages),
            client.generate(messages)
        ]
        responses = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        assert len(responses) == 3
        assert all(isinstance(r, DeepSeekResponse) for r in responses)
        assert all(r.content is not None for r in responses)

    async def test_long_conversation(self):
        """Tests handling a longer conversation context."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="system", content="You are a helpful assistant."),
            DeepSeekMessage(role="user", content="Let's talk about Python."),
            DeepSeekMessage(role="assistant", content="Python is a versatile programming language."),
            DeepSeekMessage(role="user", content="What are its key features?")
        ]

        response = await client.generate(messages)
        assert isinstance(response, DeepSeekResponse)
        assert response.content is not None
        assert len(response.content) > 50  # Should be a substantial response
        assert any(keyword in response.content.lower() for keyword in ["dynamic", "object", "interpreted"])

    async def test_error_recovery(self):
        """Tests error recovery and retry mechanism."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="user", content="Test error recovery")
        ]

        # Test with retry
        response = await client.generate_with_retry(messages, max_retries=3)
        assert isinstance(response, DeepSeekResponse)
        assert response.content is not None

    async def test_rate_limit_handling(self):
        """Tests handling of rate limits."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="user", content="Test rate limit")
        ]

        # Make rapid requests to trigger rate limit
        responses = []
        for _ in range(5):
            try:
                response = await client.generate(messages)
                responses.append(response)
            except Exception as e:
                assert "rate limit" in str(e).lower()
                break

        # Should have some successful responses
        assert len(responses) > 0
        assert all(isinstance(r, DeepSeekResponse) for r in responses)

    async def test_model_parameters(self):
        """Tests different model parameters."""
        client = DeepSeekClient()
        messages = [
            DeepSeekMessage(role="user", content="Generate a creative story.")
        ]

        # Test with different temperatures
        response_creative = await client.generate(messages, temperature=0.9)
        response_focused = await client.generate(messages, temperature=0.1)

        assert isinstance(response_creative, DeepSeekResponse)
        assert isinstance(response_focused, DeepSeekResponse)
        assert response_creative.content != response_focused.content

    async def test_response_format(self):
        """Tests response format handling."""
        client = DeepSeekClient()
        
        # Test JSON response
        messages = [
            DeepSeekMessage(
                role="system",
                content="You must respond with valid JSON containing 'name' and 'age' fields."
            ),
            DeepSeekMessage(
                role="user",
                content="Generate a person's details"
            )
        ]

        response = await client.generate(messages)
        assert isinstance(response, DeepSeekResponse)
        assert response.content is not None
        
        # Should contain JSON-like structure
        content = response.content.lower()
        assert "{" in content and "}" in content
        assert "name" in content and "age" in content

    async def test_context_handling(self):
        """Tests handling of context and memory."""
        client = DeepSeekClient()
        
        # Have a multi-turn conversation about a specific topic
        messages = [
            DeepSeekMessage(role="system", content="You are a helpful assistant."),
            DeepSeekMessage(role="user", content="My name is Alice."),
            DeepSeekMessage(role="assistant", content="Nice to meet you, Alice!"),
            DeepSeekMessage(role="user", content="What's my name?")
        ]

        response = await client.generate(messages)
        assert isinstance(response, DeepSeekResponse)
        assert "alice" in response.content.lower()

    async def test_error_cases(self):
        """Tests various error cases."""
        client = DeepSeekClient()

        # Test with empty messages
        with pytest.raises(ValueError):
            await client.generate([])

        # Test with invalid role
        with pytest.raises(ValueError):
            await client.generate([
                DeepSeekMessage(role="invalid", content="test")
            ])

        # Test with empty content
        with pytest.raises(ValueError):
            await client.generate([
                DeepSeekMessage(role="user", content="")
            ])

        # Test with invalid temperature
        with pytest.raises(ValueError):
            await client.generate(
                [DeepSeekMessage(role="user", content="test")],
                temperature=2.0
            ) 