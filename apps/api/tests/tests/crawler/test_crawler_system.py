import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.crawler.crawler import Crawler
from src.crawler.rate_limiter import RateLimiter
from src.crawler.exceptions import CrawlerError, RateLimitError

@pytest.fixture
def mock_http_client():
    with patch("aiohttp.ClientSession") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.fixture
def mock_rate_limiter():
    with patch("src.crawler.rate_limiter.RateLimiter") as mock:
        limiter = AsyncMock()
        mock.return_value = limiter
        yield limiter

@pytest.fixture
def crawler(mock_http_client, mock_rate_limiter):
    return Crawler()

@pytest.mark.asyncio
class TestCrawlerSystem:
    async def test_fetch_page(self, crawler, mock_http_client):
        """Tests basic page fetching."""
        # Setup
        url = "https://example.com"
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html>Test content</html>"
        mock_http_client.get.return_value.__aenter__.return_value = mock_response

        # Test
        content = await crawler.fetch_page(url)
        assert content == "<html>Test content</html>"
        mock_http_client.get.assert_called_once_with(url)

    async def test_fetch_page_with_rate_limit(self, crawler, mock_http_client, mock_rate_limiter):
        """Tests page fetching with rate limiting."""
        # Setup
        url = "https://example.com"
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html>Test content</html>"
        mock_http_client.get.return_value.__aenter__.return_value = mock_response

        # Test
        content = await crawler.fetch_page(url)
        assert content == "<html>Test content</html>"
        mock_rate_limiter.acquire.assert_called_once_with("example.com")

    async def test_fetch_page_rate_limit_exceeded(self, crawler, mock_rate_limiter):
        """Tests rate limit exceeded scenario."""
        # Setup
        url = "https://example.com"
        mock_rate_limiter.acquire.side_effect = RateLimitError("Rate limit exceeded")

        # Test
        with pytest.raises(RateLimitError):
            await crawler.fetch_page(url)

    async def test_fetch_page_with_retry(self, crawler, mock_http_client):
        """Tests page fetching with retry on failure."""
        # Setup
        url = "https://example.com"
        mock_response_fail = AsyncMock()
        mock_response_fail.status = 500
        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.text.return_value = "<html>Test content</html>"
        
        mock_http_client.get.return_value.__aenter__.side_effect = [
            mock_response_fail,
            mock_response_success
        ]

        # Test
        content = await crawler.fetch_page(url, max_retries=2)
        assert content == "<html>Test content</html>"
        assert mock_http_client.get.call_count == 2

    async def test_parse_html(self, crawler):
        """Tests HTML parsing."""
        # Test
        html = """
        <html>
            <body>
                <h1>Title</h1>
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <a href="https://example.com">Link</a>
            </body>
        </html>
        """
        parsed = await crawler.parse_html(html)
        assert parsed["title"] == "Title"
        assert len(parsed["paragraphs"]) == 2
        assert parsed["links"] == ["https://example.com"]

    async def test_extract_metadata(self, crawler):
        """Tests metadata extraction."""
        # Test
        html = """
        <html>
            <head>
                <meta name="description" content="Page description">
                <meta name="keywords" content="key1, key2">
                <meta property="og:title" content="OG Title">
            </head>
        </html>
        """
        metadata = await crawler.extract_metadata(html)
        assert metadata["description"] == "Page description"
        assert metadata["keywords"] == ["key1", "key2"]
        assert metadata["og_title"] == "OG Title"

    async def test_concurrent_crawling(self, crawler, mock_http_client):
        """Tests concurrent page crawling."""
        # Setup
        urls = [f"https://example.com/page{i}" for i in range(5)]
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html>Test content</html>"
        mock_http_client.get.return_value.__aenter__.return_value = mock_response

        # Test
        results = await crawler.crawl_multiple(urls)
        assert len(results) == 5
        assert all(content == "<html>Test content</html>" for content in results)
        assert mock_http_client.get.call_count == 5

    async def test_error_handling(self, crawler, mock_http_client):
        """Tests various error scenarios."""
        # Setup
        url = "https://example.com"

        # Test connection error
        mock_http_client.get.side_effect = Exception("Connection failed")
        with pytest.raises(CrawlerError):
            await crawler.fetch_page(url)

        # Test invalid URL
        with pytest.raises(ValueError):
            await crawler.fetch_page("invalid-url")

        # Test timeout
        mock_http_client.get.side_effect = asyncio.TimeoutError()
        with pytest.raises(CrawlerError):
            await crawler.fetch_page(url)

    async def test_robots_txt_compliance(self, crawler, mock_http_client):
        """Tests robots.txt compliance."""
        # Setup
        robots_txt = """
        User-agent: *
        Disallow: /private/
        Allow: /public/
        """
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = robots_txt
        mock_http_client.get.return_value.__aenter__.return_value = mock_response

        # Test
        await crawler.load_robots_txt("https://example.com")
        assert crawler.can_crawl("https://example.com/public/page") is True
        assert crawler.can_crawl("https://example.com/private/page") is False

    async def test_sitemap_parsing(self, crawler, mock_http_client):
        """Tests sitemap parsing."""
        # Setup
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
                <lastmod>2024-01-01</lastmod>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
                <lastmod>2024-01-02</lastmod>
            </url>
        </urlset>
        """
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = sitemap
        mock_http_client.get.return_value.__aenter__.return_value = mock_response

        # Test
        urls = await crawler.parse_sitemap("https://example.com/sitemap.xml")
        assert len(urls) == 2
        assert urls[0] == "https://example.com/page1"
        assert urls[1] == "https://example.com/page2"

    async def test_content_filtering(self, crawler):
        """Tests content filtering."""
        # Test
        content = """
        <html>
            <body>
                <div class="ads">Advertisement</div>
                <article>
                    <h1>Main Content</h1>
                    <p>Important text</p>
                </article>
                <div class="comments">User comments</div>
            </body>
        </html>
        """
        filtered = await crawler.filter_content(content)
        assert "Main Content" in filtered
        assert "Important text" in filtered
        assert "Advertisement" not in filtered
        assert "User comments" not in filtered 