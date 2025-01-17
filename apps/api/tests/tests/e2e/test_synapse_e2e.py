import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.router import app
from src.llm.deepseek_client import DeepSeekClient
from src.rag.rag_system import RAGSystem
from src.crawler.crawler import Crawler
from src.core.cache import CacheService
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
class TestSynapseE2E:
    async def test_basic_chat_flow(self, async_client):
        """Tests basic chat completion flow."""
        # Test request
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What is 2+2?"}
                ],
                "model": "deepseek-chat"
            }
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]
        assert data["choices"][0]["message"]["role"] == "assistant"

    async def test_streaming_chat_flow(self, async_client):
        """Tests streaming chat completion flow."""
        # Test request
        async with async_client.stream(
            "POST",
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Count from 1 to 3"}
                ],
                "model": "deepseek-chat",
                "stream": True
            }
        ) as response:
            assert response.status_code == 200
            chunks = []
            async for chunk in response.aiter_lines():
                if chunk:
                    chunks.append(chunk)
            
            # Verify streaming response
            assert len(chunks) > 0
            assert all("data: " in chunk for chunk in chunks)

    async def test_rag_enhanced_chat(self, async_client):
        """Tests chat completion with RAG context."""
        # First, index a document
        index_response = await async_client.post(
            "/v1/documents/index",
            json={
                "content": "The capital of France is Paris.",
                "metadata": {"source": "test", "type": "fact"}
            }
        )
        assert index_response.status_code == 200

        # Then, test RAG-enhanced chat
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "model": "deepseek-chat",
                "use_rag": True
            }
        )
        
        # Verify response includes RAG context
        assert response.status_code == 200
        data = response.json()
        assert "Paris" in data["choices"][0]["message"]["content"]

    async def test_error_handling(self, async_client):
        """Tests error handling in the complete flow."""
        # Test invalid model
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Test"}
                ],
                "model": "invalid-model"
            }
        )
        assert response.status_code == 400

        # Test invalid message format
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": "invalid",
                "model": "deepseek-chat"
            }
        )
        assert response.status_code == 422

        # Test rate limiting
        responses = await asyncio.gather(
            *[async_client.post(
                "/v1/chat/completions",
                headers={"test-name": "test_error_handling"},
                json={
                    "messages": [{"role": "user", "content": "Test"}],
                    "model": "deepseek-chat"
                }
            ) for _ in range(10)]
        )
        assert any(r.status_code == 429 for r in responses)

    async def test_document_management(self, async_client):
        """Tests document indexing and retrieval flow."""
        # Index document
        doc_id = None
        index_response = await async_client.post(
            "/v1/documents/index",
            json={
                "content": "Test document content",
                "metadata": {"source": "test"}
            }
        )
        assert index_response.status_code == 200
        doc_id = index_response.json()["document_id"]

        # Retrieve document
        get_response = await async_client.get(f"/v1/documents/{doc_id}")
        assert get_response.status_code == 200
        assert get_response.json()["content"] == "Test document content"

        # Search documents
        search_response = await async_client.post(
            "/v1/documents/search",
            json={
                "query": "test document",
                "limit": 5
            }
        )
        assert search_response.status_code == 200
        results = search_response.json()["results"]
        assert len(results) > 0
        assert any(r["document_id"] == doc_id for r in results)

    async def test_conversation_memory(self, async_client):
        """Tests conversation memory and context maintenance."""
        # First message
        response1 = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "My name is John"}
                ],
                "model": "deepseek-chat"
            }
        )
        assert response1.status_code == 200

        # Follow-up message
        response2 = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "My name is John"},
                    {"role": "assistant", "content": response1.json()["choices"][0]["message"]["content"]},
                    {"role": "user", "content": "What's my name?"}
                ],
                "model": "deepseek-chat"
            }
        )
        assert response2.status_code == 200
        assert "John" in response2.json()["choices"][0]["message"]["content"]

    async def test_system_integration(self, async_client):
        """Tests integration of all system components."""
        # 1. Crawl and index content
        crawl_response = await async_client.post(
            "/v1/crawler/crawl",
            json={
                "url": "https://example.com",
                "index_content": True
            }
        )
        assert crawl_response.status_code == 200

        # 2. Search indexed content
        search_response = await async_client.post(
            "/v1/documents/search",
            json={
                "query": "example",
                "limit": 5
            }
        )
        assert search_response.status_code == 200

        # 3. Use content in chat
        chat_response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "What did we learn from example.com?"}
                ],
                "model": "deepseek-chat",
                "use_rag": True
            }
        )
        assert chat_response.status_code == 200

    async def test_performance_requirements(self, async_client):
        """Tests system performance requirements."""
        # Measure response time for chat completion
        start_time = asyncio.get_event_loop().time()
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Quick test"}
                ],
                "model": "deepseek-chat"
            }
        )
        end_time = asyncio.get_event_loop().time()
        assert end_time - start_time < 5  # Response within 5 seconds

        # Test concurrent requests handling
        start_time = asyncio.get_event_loop().time()
        responses = await asyncio.gather(
            *[async_client.post(
                "/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": f"Test {i}"}],
                    "model": "deepseek-chat"
                }
            ) for i in range(5)]
        )
        end_time = asyncio.get_event_loop().time()
        
        assert all(r.status_code == 200 for r in responses)
        assert end_time - start_time < 10  # All responses within 10 seconds 

    async def test_authentication_flow(self, async_client):
        """Tests complete authentication flow."""
        # Test registration
        register_response = await async_client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!@#",
                "name": "Test User"
            }
        )
        assert register_response.status_code == 201

        # Test login
        login_response = await async_client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Test protected route access
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = await async_client.get(
            "/v1/user/profile",
            headers=headers
        )
        assert protected_response.status_code == 200

        # Test invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        invalid_response = await async_client.get(
            "/v1/user/profile",
            headers=invalid_headers
        )
        assert invalid_response.status_code == 401

        # Test logout
        logout_response = await async_client.post(
            "/v1/auth/logout",
            headers=headers
        )
        assert logout_response.status_code == 200

        # Verify can't access protected route after logout
        post_logout_response = await async_client.get(
            "/v1/user/profile",
            headers=headers
        )
        assert post_logout_response.status_code == 401

    async def test_rate_limiting(self, async_client):
        """Tests rate limiting functionality."""
        # Login to get token
        login_response = await async_client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "test-name": "test_rate_limiting"
        }

        # Make multiple requests to trigger rate limit
        responses = await asyncio.gather(
            *[async_client.post(
                "/v1/chat/completions",
                headers=headers,
                json={
                    "messages": [{"role": "user", "content": f"Test {i}"}],
                    "model": "deepseek-chat"
                }
            ) for i in range(110)]  # Assuming rate limit is 100 requests
        )

        # Verify some requests were rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        assert success_count <= 100  # Maximum allowed requests
        assert rate_limited_count > 0  # Some requests were rate limited

    async def test_security_headers(self, async_client):
        """Tests security headers and configurations."""
        response = await async_client.get("/v1/health")
        headers = response.headers

        # Verify security headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in headers
        assert "Strict-Transport-Security" in headers

    async def test_input_validation(self, async_client):
        """Tests input validation and sanitization."""
        # Test SQL injection attempt
        sql_injection_response = await async_client.post(
            "/v1/auth/login",
            json={
                "email": "' OR '1'='1",
                "password": "' OR '1'='1"
            }
        )
        assert sql_injection_response.status_code in (400, 401)

        # Test XSS attempt
        xss_response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "<script>alert('xss')</script>"}],
                "model": "deepseek-chat"
            }
        )
        assert xss_response.status_code == 200
        assert "<script>" not in xss_response.json()["choices"][0]["message"]["content"]

        # Test invalid JSON
        invalid_json_response = await async_client.post(
            "/v1/chat/completions",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert invalid_json_response.status_code == 422 