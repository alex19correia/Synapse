"""
Web crawler implementation for content extraction.
"""
import aiohttp
import asyncio
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from ..analytics.metrics.crawler_metrics import CrawlerMetrics
from ..utils.rate_limiter import RateLimiter

class Crawler:
    """
    Asynchronous web crawler with rate limiting and metrics tracking.
    """
    
    def __init__(self, rate_limit: int = 10, period: int = 60):
        """
        Initialize the crawler.
        
        Args:
            rate_limit: Maximum requests per period
            period: Time period in seconds
        """
        self.rate_limiter = RateLimiter(rate_limit, period)
        self.metrics = CrawlerMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()
            
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a single page with rate limiting and metrics.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content if successful, None otherwise
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            await self.rate_limiter.acquire()
            
            async with self.metrics.track_request(url=url):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
                    
        except Exception as e:
            self.metrics.track_error(url=url, error=str(e))
            return None
            
    async def extract_content(self, html: str) -> Dict[str, str]:
        """
        Extract content from HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Dictionary with extracted content
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style']):
            element.decompose()
            
        return {
            'title': soup.title.string if soup.title else '',
            'text': soup.get_text(separator=' ', strip=True),
            'links': [a.get('href', '') for a in soup.find_all('a', href=True)]
        }
        
    async def crawl(self, start_url: str, max_pages: int = 10) -> List[Dict[str, str]]:
        """
        Crawl pages starting from a URL.
        
        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl
            
        Returns:
            List of extracted content from pages
        """
        results = []
        visited = set()
        queue = [start_url]
        
        async with self:
            while queue and len(visited) < max_pages:
                url = queue.pop(0)
                if url in visited:
                    continue
                    
                content = await self.fetch_page(url)
                if content:
                    extracted = await self.extract_content(content)
                    extracted['url'] = url
                    results.append(extracted)
                    
                    # Add new URLs to queue
                    for link in extracted['links']:
                        full_url = urljoin(url, link)
                        if full_url not in visited:
                            queue.append(full_url)
                            
                visited.add(url)
                
        return results 