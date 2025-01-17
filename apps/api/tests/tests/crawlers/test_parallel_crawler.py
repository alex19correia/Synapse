"""Tests for the parallel crawler module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from httpx import Response
from src.crawlers.parallel_crawler import ParallelCrawler, WebContent

# Fixtures
@pytest.fixture
def mock_metrics():
    metrics = Mock()
    metrics.track_crawl = AsyncMock()
    metrics.track_error = AsyncMock()
    metrics.set_active_crawls = AsyncMock()
    return metrics

@pytest.fixture
def mock_client():
    client = Mock()
    client.get = AsyncMock()
    client.aclose = AsyncMock()
    return client

@pytest.fixture
async def crawler(mock_metrics, mock_client):
    with patch("src.crawlers.parallel_crawler.CrawlerMetrics") as MockMetrics, \
         patch("src.crawlers.parallel_crawler.httpx.AsyncClient") as MockClient:
        MockMetrics.return_value = mock_metrics
        MockClient.return_value = mock_client
        crawler = ParallelCrawler(concurrency=2, timeout=10)
        yield crawler
        await crawler.close()

# Tests
@pytest.mark.asyncio
async def test_crawl_url_success(crawler, mock_client, mock_metrics):
    """Test successful crawling of a single URL."""
    url = "https://example.com"
    mock_response = Mock(spec=Response)
    mock_response.text = "Test content"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response

    result = await crawler.crawl_url(url)

    assert isinstance(result, WebContent)
    assert result.url == url
    assert result.content == "Test content"
    assert result.status_code == 200
    assert result.headers == {"content-type": "text/html"}
    assert "duration" in result.metadata
    assert "size" in result.metadata

    mock_metrics.track_crawl.assert_awaited_once()
    mock_client.get.assert_awaited_once_with(url)

@pytest.mark.asyncio
async def test_crawl_url_error(crawler, mock_client, mock_metrics):
    """Test error handling when crawling a URL."""
    url = "https://example.com"
    mock_client.get.side_effect = Exception("Connection error")

    result = await crawler.crawl_url(url)

    assert result is None
    mock_metrics.track_error.assert_awaited_once()
    mock_client.get.assert_awaited_once_with(url)

@pytest.mark.asyncio
async def test_crawl_urls_parallel(crawler, mock_client, mock_metrics):
    """Test parallel crawling of multiple URLs."""
    urls = ["https://example1.com", "https://example2.com"]
    mock_response = Mock(spec=Response)
    mock_response.text = "Test content"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response

    results = await crawler.crawl_urls(urls)

    assert len(results) == 2
    assert all(isinstance(r, WebContent) for r in results)
    mock_metrics.set_active_crawls.assert_awaited_once_with(2)
    assert mock_client.get.await_count == 2

@pytest.mark.asyncio
async def test_crawl_urls_with_errors(crawler, mock_client, mock_metrics):
    """Test parallel crawling with some failed requests."""
    urls = ["https://example1.com", "https://example2.com"]
    mock_response = Mock(spec=Response)
    mock_response.text = "Test content"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"Test content"
    
    def get_side_effect(url):
        if url == "https://example1.com":
            return mock_response
        raise Exception("Connection error")
    
    mock_client.get.side_effect = get_side_effect

    results = await crawler.crawl_urls(urls)

    assert len(results) == 1
    assert results[0].url == "https://example1.com"
    assert mock_metrics.track_error.await_count == 1
    assert mock_metrics.track_crawl.await_count == 1

@pytest.mark.asyncio
async def test_client_lifecycle(crawler, mock_client):
    """Test proper client initialization and cleanup."""
    await crawler.close()
    mock_client.aclose.assert_awaited_once()

@pytest.mark.asyncio
async def test_metrics_integration(crawler, mock_client, mock_metrics):
    """Test proper integration with metrics tracking."""
    url = "https://example.com"
    mock_response = Mock(spec=Response)
    mock_response.text = "Test content"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response

    await crawler.crawl_url(url)

    # Verify metrics were tracked
    mock_metrics.track_crawl.assert_awaited_once()
    args = mock_metrics.track_crawl.call_args[1]
    assert args["url"] == url
    assert args["status"] == 200
    assert isinstance(args["duration"], float)
    assert args["size"] == len(b"Test content") 