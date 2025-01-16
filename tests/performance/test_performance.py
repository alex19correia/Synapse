import pytest
import asyncio
import time
import statistics
from unittest.mock import AsyncMock, patch
from src.api.router import app
from src.llm.deepseek_client import DeepSeekClient
from src.rag.rag_system import RAGSystem
from src.crawler.crawler import Crawler
from src.core.cache import Cache
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.performance
class TestPerformance:
    async def test_chat_completion_latency(self, async_client):
        """Tests chat completion latency under normal conditions."""
        latencies = []
        
        # Perform multiple requests and measure latency
        for _ in range(50):
            start_time = time.time()
            response = await async_client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": "What is 2+2?"}
                    ],
                    "model": "deepseek-chat"
                }
            )
            end_time = time.time()
            assert response.status_code == 200
            latencies.append(end_time - start_time)
            
            # Add small delay between requests
            await asyncio.sleep(0.1)
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        
        # Assert performance requirements
        assert avg_latency < 1.0  # Average latency under 1 second
        assert p95_latency < 2.0  # 95% of requests under 2 seconds
        assert p99_latency < 3.0  # 99% of requests under 3 seconds

    async def test_concurrent_load(self, async_client):
        """Tests system performance under concurrent load."""
        # Test different concurrency levels
        concurrency_levels = [5, 10, 20]
        
        for concurrency in concurrency_levels:
            start_time = time.time()
            responses = await asyncio.gather(
                *[async_client.post(
                    "/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "user", "content": f"Test message {i}"}
                        ],
                        "model": "deepseek-chat"
                    }
                ) for i in range(concurrency)]
            )
            end_time = time.time()
            
            # Calculate throughput
            duration = end_time - start_time
            requests_per_second = concurrency / duration
            
            # Verify all requests succeeded
            assert all(r.status_code == 200 for r in responses)
            
            # Assert minimum throughput
            assert requests_per_second >= concurrency / 5  # Minimum throughput requirement

    async def test_rag_performance(self, async_client):
        """Tests RAG system performance."""
        # First, index test documents
        docs = [
            {
                "content": f"Test document {i} content with specific information.",
                "metadata": {"source": "test", "type": "performance"}
            }
            for i in range(100)
        ]
        
        # Measure indexing performance
        start_time = time.time()
        for doc in docs:
            response = await async_client.post("/v1/documents/index", json=doc)
            assert response.status_code == 200
        indexing_time = time.time() - start_time
        
        # Assert indexing performance
        assert indexing_time / len(docs) < 0.5  # Average indexing time per document
        
        # Test search performance
        search_latencies = []
        for _ in range(20):
            start_time = time.time()
            response = await async_client.post(
                "/v1/documents/search",
                json={
                    "query": "specific information",
                    "limit": 5
                }
            )
            search_latencies.append(time.time() - start_time)
            assert response.status_code == 200
            
        # Assert search performance
        avg_search_latency = statistics.mean(search_latencies)
        assert avg_search_latency < 0.5  # Average search latency under 0.5 seconds

    async def test_memory_usage(self, async_client):
        """Tests memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate load
        for _ in range(50):
            response = await async_client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": "Test message with some length to it"}
                    ],
                    "model": "deepseek-chat"
                }
            )
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assert reasonable memory usage
        assert memory_increase < 100  # Memory increase under 100MB

    async def test_stress_test(self, async_client):
        """Tests system behavior under stress."""
        # Prepare test data
        test_messages = [
            "Short message",
            "Medium length message with some content",
            "A longer message that contains more words and should require more processing time",
            "A very long message " * 10
        ]
        
        results = {
            "success": 0,
            "errors": 0,
            "timeouts": 0
        }
        
        # Run stress test
        async def stress_request(message):
            try:
                start_time = time.time()
                response = await async_client.post(
                    "/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "user", "content": message}
                        ],
                        "model": "deepseek-chat"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    results["success"] += 1
                else:
                    results["errors"] += 1
                return time.time() - start_time
            except asyncio.TimeoutError:
                results["timeouts"] += 1
                return None
        
        # Run 100 requests with different message lengths
        latencies = []
        tasks = []
        for _ in range(25):  # 25 requests of each length
            for message in test_messages:
                tasks.append(stress_request(message))
        
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        latencies = [l for l in completed if l is not None]
        
        # Assert stress test results
        success_rate = results["success"] / (results["success"] + results["errors"] + results["timeouts"])
        assert success_rate > 0.95  # 95% success rate
        assert results["timeouts"] < 5  # Less than 5 timeouts
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            assert avg_latency < 2.0  # Average latency under 2 seconds

    async def test_cache_performance(self, async_client):
        """Tests cache system performance."""
        # Test cache hit performance
        cache_latencies = []
        
        # First request (cache miss)
        response = await async_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "This should be cached"}
                ],
                "model": "deepseek-chat"
            }
        )
        assert response.status_code == 200
        
        # Subsequent requests (cache hits)
        for _ in range(20):
            start_time = time.time()
            response = await async_client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": "This should be cached"}
                    ],
                    "model": "deepseek-chat"
                }
            )
            cache_latencies.append(time.time() - start_time)
            assert response.status_code == 200
        
        # Assert cache performance
        avg_cache_latency = statistics.mean(cache_latencies)
        assert avg_cache_latency < 0.1  # Cache hits should be very fast

    async def test_long_running_stability(self, async_client):
        """Tests system stability over a longer period."""
        start_time = time.time()
        end_time = start_time + 300  # 5 minutes test
        
        success_count = 0
        error_count = 0
        
        while time.time() < end_time:
            try:
                response = await async_client.post(
                    "/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "user", "content": "Test message"}
                        ],
                        "model": "deepseek-chat"
                    }
                )
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
            
            await asyncio.sleep(1)  # 1 request per second
        
        # Calculate reliability metrics
        total_requests = success_count + error_count
        reliability = success_count / total_requests if total_requests > 0 else 0
        
        # Assert long-running stability
        assert reliability > 0.99  # 99% reliability over extended period
        assert error_count < total_requests * 0.01  # Less than 1% errors 