from typing import List, Optional, Dict, Any
import asyncio
import httpx
from datetime import datetime
from pydantic import BaseModel, Field
from src.utils.logger import get_logger
from src.analytics.metrics.crawler_metrics import CrawlerMetrics

logger = get_logger("parallel_crawler")

class WebContent(BaseModel):
    url: str
    content: str
    status_code: int
    headers: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class ParallelCrawler:
    def __init__(self, concurrency: int = 5, timeout: int = 30):
        self.concurrency = concurrency
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.metrics = CrawlerMetrics()
        
    async def crawl_url(self, url: str) -> Optional[WebContent]:
        try:
            start_time = datetime.now()
            response = await self.client.get(url)
            duration = (datetime.now() - start_time).total_seconds()
            
            await self.metrics.track_crawl(
                url=url,
                status=response.status_code,
                duration=duration,
                size=len(response.content)
            )
            
            return WebContent(
                url=url,
                content=response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
                metadata={
                    "duration": duration,
                    "size": len(response.content)
                }
            )
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            await self.metrics.track_error(url=url, error=str(e))
            return None
            
    async def crawl_urls(self, urls: List[str]) -> List[WebContent]:
        await self.metrics.set_active_crawls(len(urls))
        tasks = [self.crawl_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if r is not None]
        
    async def close(self):
        await self.client.aclose() 