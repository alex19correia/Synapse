"""Tests for the base Crawler class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientResponse
from contextlib import asynccontextmanager
from src.crawler.crawler import Crawler
from src.analytics.metrics.crawler_metrics import CrawlerMetrics
from src.utils.rate_limiter import RateLimiter

@asynccontextmanager
async def async_mock_cm(mock_obj):
    """Helper function to create async context managers."""
    yield mock_obj

@pytest.fixture
def mock_rate_limiter():
    """Fixture for mocked rate limiter."""
    limiter = AsyncMock(spec=RateLimiter)
    limiter.acquire = AsyncMock()
    return limiter

@pytest.fixture
def mock_metrics():
    """Fixture for mocked crawler metrics."""
    metrics = Mock(spec=CrawlerMetrics)
    metrics.track_request = Mock(return_value=async_mock_cm(None))
    metrics.track_error = Mock()
    return metrics

@pytest.fixture
def mock_response():
    """Fixture for mocked HTTP response."""
    response = AsyncMock(spec=ClientResponse)
    response.status = 200
    response.text = AsyncMock()
    return response

@pytest.fixture
def mock_session(mock_response):
    """Fixture for mocked aiohttp session."""
    session = AsyncMock(spec=ClientSession)
    session.get = Mock(return_value=async_mock_cm(mock_response))
    session.close = AsyncMock()
    return session

@pytest.fixture
async def crawler(mock_metrics, mock_rate_limiter):
    """Fixture for crawler instance with mocked dependencies."""
    with patch('src.crawler.crawler.CrawlerMetrics', return_value=mock_metrics), \
         patch('src.crawler.crawler.RateLimiter', return_value=mock_rate_limiter):
        crawler = Crawler(rate_limit=10, period=60)
        yield crawler
        if crawler.session:
            await crawler.session.close()

@pytest.mark.asyncio
async def test_crawler_initialization(crawler):
    """Test crawler initialization with default parameters."""
    assert crawler.rate_limiter is not None
    assert crawler.metrics is not None
    assert crawler.session is None

@pytest.mark.asyncio
async def test_context_manager():
    """Test crawler as context manager."""
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = AsyncMock(spec=ClientSession)
        mock_session.close = AsyncMock()
        mock_session_class.return_value = mock_session
        
        async with Crawler() as crawler:
            assert isinstance(crawler, Crawler)
            assert crawler.session is not None
        
        mock_session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_fetch_page_success(crawler, mock_session, mock_response):
    """Test successful page fetch."""
    url = "https://example.com"
    html_content = "<html><body>Test content</body></html>"
    mock_response.text = AsyncMock()
    mock_response.text.return_value = html_content
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        content = await crawler.fetch_page(url)
        
    assert content == html_content
    crawler.rate_limiter.acquire.assert_awaited_once()
    assert mock_session.get.called
    assert crawler.metrics.track_request.called

@pytest.mark.asyncio
async def test_fetch_page_error(crawler, mock_session):
    """Test page fetch with error."""
    url = "https://example.com"
    mock_session.get.side_effect = Exception("Connection error")
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        content = await crawler.fetch_page(url)
        
    assert content is None
    crawler.metrics.track_error.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_page_non_200(crawler, mock_session, mock_response):
    """Test page fetch with non-200 status code."""
    url = "https://example.com"
    mock_response.status = 404
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        content = await crawler.fetch_page(url)
        
    assert content is None

@pytest.mark.asyncio
async def test_extract_content(crawler):
    """Test content extraction from HTML."""
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <script>console.log('remove me');</script>
            <p>Test content</p>
            <a href="/link1">Link 1</a>
            <a href="https://example.com/link2">Link 2</a>
        </body>
    </html>
    """
    
    content = await crawler.extract_content(html)
    
    assert content['title'] == 'Test Page'
    assert 'Test content' in content['text']
    assert 'console.log' not in content['text']
    assert len(content['links']) == 2
    assert '/link1' in content['links']
    assert 'https://example.com/link2' in content['links']

@pytest.mark.asyncio
async def test_crawl_basic(crawler, mock_session, mock_response):
    """Test basic crawling functionality."""
    start_url = "https://example.com"
    html_content = """
    <html>
        <head><title>Test</title></head>
        <body>
            <p>Content</p>
            <a href="/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
        </body>
    </html>
    """
    mock_response.text = AsyncMock()
    mock_response.text.return_value = html_content
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        results = await crawler.crawl(start_url, max_pages=2)
        
    assert len(results) > 0
    assert all('url' in result for result in results)
    assert all('title' in result for result in results)
    assert all('text' in result for result in results)
    assert all('links' in result for result in results)

@pytest.mark.asyncio
async def test_crawl_max_pages(crawler, mock_session, mock_response):
    """Test crawling respects max_pages limit."""
    start_url = "https://example.com"
    html_content = """
    <html>
        <head><title>Test</title></head>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="/page3">Page 3</a>
        </body>
    </html>
    """
    mock_response.text = AsyncMock()
    mock_response.text.return_value = html_content
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        results = await crawler.crawl(start_url, max_pages=2)
        
    assert len(results) <= 2

@pytest.mark.asyncio
async def test_crawl_cycle_detection(crawler, mock_session, mock_response):
    """Test crawling handles cycles in links."""
    start_url = "https://example.com"
    html_content = """
    <html>
        <head><title>Test</title></head>
        <body>
            <a href="https://example.com">Self link</a>
            <a href="https://example.com/page1">Page 1</a>
        </body>
    </html>
    """
    mock_response.text = AsyncMock()
    mock_response.text.return_value = html_content
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        results = await crawler.crawl(start_url, max_pages=3)
        
    # Should not get stuck in a loop
    assert len(results) > 0
    # Should not visit the same URL twice
    urls = [result['url'] for result in results]
    assert len(urls) == len(set(urls)) 