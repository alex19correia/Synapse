"""Tests for the ParallelCrawler class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import httpx
from datetime import datetime
from src.crawlers.parallel_crawler import ParallelCrawler, WebContent
from src.analytics.metrics.crawler_metrics import CrawlerMetrics

@pytest.fixture
def mock_metrics():
    """Fixture for mocked crawler metrics."""
    metrics = AsyncMock(spec=CrawlerMetrics)
    metrics.track_crawl = AsyncMock()
    metrics.track_error = AsyncMock()
    metrics.set_active_crawls = AsyncMock()
    return metrics

@pytest.fixture
def mock_client():
    """Fixture for mocked httpx client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get = AsyncMock()
    client.aclose = AsyncMock()
    return client

@pytest.fixture
async def crawler(mock_metrics, mock_client):
    """Fixture for crawler instance with mocked dependencies."""
    with patch('src.crawlers.parallel_crawler.CrawlerMetrics', return_value=mock_metrics), \
         patch('httpx.AsyncClient', return_value=mock_client):
        crawler = ParallelCrawler(concurrency=5, timeout=30)
        yield crawler
        await crawler.close()

@pytest.mark.asyncio
async def test_crawler_initialization():
    """Test crawler initialization with default parameters."""
    crawler = ParallelCrawler()
    assert crawler.concurrency == 5  # Default value
    assert crawler.timeout == 30  # Default value
    assert isinstance(crawler.metrics, CrawlerMetrics)
    await crawler.close()

@pytest.mark.asyncio
async def test_crawler_custom_params():
    """Test crawler initialization with custom parameters."""
    crawler = ParallelCrawler(concurrency=10, timeout=60)
    assert crawler.concurrency == 10
    assert crawler.timeout == 60
    await crawler.close()

@pytest.mark.asyncio
async def test_crawl_url_success(crawler, mock_client):
    """Test successful URL crawl."""
    url = "https://example.com"
    content = "Test content"
    headers = {"content-type": "text/html"}
    
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.text = content
    mock_response.status_code = 200
    mock_response.headers = headers
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response
    
    result = await crawler.crawl_url(url)
    
    assert isinstance(result, WebContent)
    assert result.url == url
    assert result.content == content
    assert result.status_code == 200
    assert result.headers == headers
    assert isinstance(result.timestamp, datetime)
    
    crawler.metrics.track_crawl.assert_awaited_once()
    mock_client.get.assert_awaited_once_with(url)

@pytest.mark.asyncio
async def test_crawl_url_error(crawler, mock_client):
    """Test URL crawl with error."""
    url = "https://example.com"
    mock_client.get.side_effect = Exception("Connection error")
    
    result = await crawler.crawl_url(url)
    
    assert result is None
    crawler.metrics.track_error.assert_awaited_once()

@pytest.mark.asyncio
async def test_crawl_urls_parallel(crawler, mock_client):
    """Test parallel crawling of multiple URLs."""
    urls = [f"https://example.com/page{i}" for i in range(3)]
    content = "Test content"
    headers = {"content-type": "text/html"}
    
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.text = content
    mock_response.status_code = 200
    mock_response.headers = headers
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response
    
    results = await crawler.crawl_urls(urls)
    
    assert len(results) == len(urls)
    assert all(isinstance(r, WebContent) for r in results)
    assert all(r.content == content for r in results)
    
    crawler.metrics.set_active_crawls.assert_awaited_once_with(len(urls))
    assert mock_client.get.await_count == len(urls)

@pytest.mark.asyncio
async def test_crawl_urls_mixed_results(crawler, mock_client):
    """Test parallel crawling with mix of successes and failures."""
    urls = [f"https://example.com/page{i}" for i in range(3)]
    
    async def mock_get(url):
        if "page0" in url:
            raise Exception("Connection error")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.text = "Test content"
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.content = b"Test content"
        return mock_response
    
    mock_client.get.side_effect = mock_get
    
    results = await crawler.crawl_urls(urls)
    
    assert len(results) == 2  # One failed, two succeeded
    assert all(isinstance(r, WebContent) for r in results)
    
    assert crawler.metrics.track_error.await_count == 1
    assert crawler.metrics.track_crawl.await_count == 2

@pytest.mark.asyncio
async def test_client_lifecycle(mock_metrics):
    """Test proper client lifecycle management."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.aclose = AsyncMock()
        mock_client_class.return_value = mock_client
        
        crawler = ParallelCrawler()
        await crawler.close()
        
        mock_client.aclose.assert_awaited_once()

@pytest.mark.asyncio
async def test_metrics_integration(crawler, mock_client):
    """Test integration with metrics system."""
    url = "https://example.com"
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.text = "Test content"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"Test content"
    mock_client.get.return_value = mock_response
    
    await crawler.crawl_url(url)
    
    # Verify metrics were tracked
    assert crawler.metrics.track_crawl.await_count == 1
    args = crawler.metrics.track_crawl.await_args[1]
    assert args['url'] == url
    assert args['status'] == 200
    assert isinstance(args['duration'], float)
    assert isinstance(args['size'], int) 