import pytest
import asyncio
from src.crawlers.parallel_crawler import ParallelCrawler
from src.crawlers.config import CrawlerConfig
from src.crawlers.rate_limiter import RateLimiter, RateLimitConfig
from src.crawlers.cache import DistributedCache, CacheConfig

@pytest.fixture
async def redis_url():
    return "redis://localhost"

@pytest.fixture
async def rate_limiter(redis_url):
    config = RateLimitConfig(
        requests_per_second=5,
        max_requests_per_domain=10,
        cooldown_period=30
    )
    limiter = RateLimiter(redis_url, config)
    yield limiter
    await limiter.close()

@pytest.fixture
async def cache(redis_url):
    config = CacheConfig(
        enabled=True,
        ttl=300,
        max_size="100MB"
    )
    cache = DistributedCache(redis_url, config)
    yield cache
    await cache.close()

@pytest.fixture
async def crawler(rate_limiter, cache):
    config = CrawlerConfig(
        max_concurrent=2,
        batch_size=5,
        browser_settings={
            "headless": True,
            "timeout": 10000
        }
    )
    crawler = ParallelCrawler(
        config=config,
        rate_limiter=rate_limiter,
        cache=cache
    )
    return crawler

@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawler_with_rate_limit(crawler, rate_limiter):
    """Testa crawler com rate limiting"""
    urls = [
        "https://example.com",
        "https://example.com/page1",
        "https://example.com/page2"
    ]
    
    result = await crawler.crawl_urls(urls)
    assert result["metrics"]["crawl"]["total_urls"] == len(urls)
    assert result["metrics"]["crawl"]["success"] > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawler_with_cache(crawler, cache):
    """Testa crawler com cache"""
    url = "https://example.com"
    
    # Primeira requisição
    result1 = await crawler.crawl_urls([url])
    assert result1["metrics"]["crawl"]["success"] == 1
    
    # Segunda requisição (deve usar cache)
    result2 = await crawler.crawl_urls([url])
    assert result2["metrics"]["crawl"]["success"] == 1
    
    # Conteúdo deve ser igual
    assert result1["content"][0].dict() == result2["content"][0].dict()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawler_parallel_processing(crawler):
    """Testa processamento paralelo do crawler"""
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    start_time = asyncio.get_event_loop().time()
    result = await crawler.crawl_urls(urls)
    end_time = asyncio.get_event_loop().time()
    
    # Tempo total deve ser menor que processamento sequencial
    assert end_time - start_time < len(urls) * 5  # 5 segundos por URL
    assert result["metrics"]["crawl"]["total_urls"] == len(urls)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawler_error_handling(crawler):
    """Testa tratamento de erros do crawler"""
    urls = [
        "https://invalid-url-that-does-not-exist.com",
        "https://example.com"
    ]
    
    result = await crawler.crawl_urls(urls)
    assert result["metrics"]["crawl"]["errors"] == 1
    assert result["metrics"]["crawl"]["success"] == 1 