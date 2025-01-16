# Sistema de Crawlers 🕷️

## Visão Geral

O sistema de Crawlers do Synapse Assistant é responsável por coletar, processar e indexar conteúdo de diversas fontes web de forma eficiente e escalável.

## Componentes

### 1. Base Crawler
```python
from src.crawlers.base import BaseCrawler

class CustomCrawler(BaseCrawler):
    async def crawl(self, url: str) -> Document:
        # Fetch content
        content = await self.fetch(url)
        
        # Process content
        document = await self.process(content)
        
        return document
```

### 2. Fetcher System
```python
class ContentFetcher:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        
    async def fetch(self, url: str) -> str:
        response = await self.client.get(url)
        return response.text
```

## Tipos de Crawlers

### 1. Web Crawler
```python
class WebCrawler(BaseCrawler):
    async def crawl_site(self, url: str, max_depth: int = 3):
        # Get initial page
        content = await self.fetch(url)
        
        # Extract links
        links = self.extract_links(content)
        
        # Crawl recursively
        for link in links:
            if self.should_crawl(link):
                await self.crawl(link)
```

### 2. API Crawler
```python
class APICrawler(BaseCrawler):
    async def crawl_api(self, endpoint: str, params: dict):
        # Make API request
        data = await self.client.get(endpoint, params=params)
        
        # Process response
        document = self.process_response(data)
        
        return document
```

## Processamento

### 1. Content Processor
```python
class ContentProcessor:
    async def process(self, content: str) -> Document:
        # Clean HTML
        text = self.clean_html(content)
        
        # Extract metadata
        metadata = self.extract_metadata(content)
        
        # Create document
        document = Document(
            text=text,
            metadata=metadata
        )
        
        return document
```

### 2. Link Extractor
```python
class LinkExtractor:
    def extract_links(self, content: str) -> list[str]:
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract links
        links = [
            a['href'] for a in soup.find_all('a', href=True)
            if self.is_valid_link(a['href'])
        ]
        
        return links
```

## Rate Limiting

### 1. Rate Limiter
```python
class RateLimiter:
    def __init__(self, requests_per_second: float):
        self.rate = requests_per_second
        self.tokens = TokenBucket(rate=self.rate)
    
    async def acquire(self):
        await self.tokens.acquire()
```

### 2. Delay Manager
```python
class DelayManager:
    async def delay_request(self, domain: str):
        delay = self.get_domain_delay(domain)
        await asyncio.sleep(delay)
```

## Armazenamento

### 1. Document Store
```python
class DocumentStore:
    async def store_document(self, document: Document):
        # Prepare document
        doc_data = self.prepare_document(document)
        
        # Store in database
        await self.db.documents.insert_one(doc_data)
```

### 2. Cache Manager
```python
class CacheManager:
    async def cache_content(self, url: str, content: str):
        # Generate cache key
        key = self.generate_key(url)
        
        # Store in cache
        await self.redis.set(key, content, ex=3600)
```

## Monitoramento

### 1. Crawler Monitor
```python
class CrawlerMonitor:
    async def monitor_crawl(self, crawler: BaseCrawler):
        # Track requests
        await self.track_requests(crawler)
        
        # Monitor performance
        await self.track_performance(crawler)
        
        # Log errors
        await self.log_errors(crawler)
```

### 2. Performance Tracker
```python
class PerformanceTracker:
    async def track_metrics(self, metrics: dict):
        # Track latency
        await self.track_latency(metrics["latency"])
        
        # Track success rate
        await self.track_success_rate(metrics["success"])
        
        # Track resource usage
        await self.track_resources(metrics["resources"])
```

## Políticas

### 1. Robots.txt Parser
```python
class RobotsParser:
    async def check_allowed(self, url: str) -> bool:
        # Get robots.txt
        robots = await self.fetch_robots(url)
        
        # Parse rules
        rules = self.parse_rules(robots)
        
        # Check if allowed
        return self.is_allowed(url, rules)
```

### 2. Policy Enforcer
```python
class PolicyEnforcer:
    def enforce_policies(self, url: str) -> bool:
        # Check robots.txt
        if not self.check_robots(url):
            return False
            
        # Check rate limits
        if not self.check_rate_limits(url):
            return False
            
        return True
```

## Métricas

### 1. Crawler Metrics
```python
class CrawlerMetrics:
    async def track_crawl(self, url: str, result: CrawlResult):
        metrics = {
            "url": url,
            "status": result.status,
            "duration": result.duration,
            "size": len(result.content)
        }
        await self.save_metrics(metrics)
```

### 2. Error Tracking
```python
class ErrorTracker:
    async def track_error(self, error: Exception, context: dict):
        error_data = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": current_time()
        }
        await self.save_error(error_data)
```

## Configuração

### 1. Crawler Config
```yaml
crawler:
  concurrency: 10
  max_depth: 3
  rate_limit: 1.0
  timeout: 30
  retries: 3
  user_agent: "Synapse Crawler/1.0"
```

### 2. Domain Config
```yaml
domains:
  example.com:
    rate_limit: 0.5
    max_depth: 5
    allowed_paths:
      - /docs
      - /blog
    excluded_paths:
      - /admin
      - /private
```

## Manutenção

### 1. Health Checks
```python
class HealthChecker:
    async def check_health(self) -> Health:
        # Check connections
        connections = await self.check_connections()
        
        # Check rate limits
        rate_limits = await self.check_rate_limits()
        
        # Check storage
        storage = await self.check_storage()
        
        return Health(
            connections=connections,
            rate_limits=rate_limits,
            storage=storage
        )
```

### 2. Maintenance Tasks
```python
class MaintenanceTasks:
    async def perform_maintenance(self):
        # Clean cache
        await self.clean_cache()
        
        # Update robots.txt
        await self.update_robots()
        
        # Optimize storage
        await self.optimize_storage()
```

## Referências

- [Scrapy Documentation](https://docs.scrapy.org/)
- [robots.txt Specification](https://www.robotstxt.org/robotstxt.html)
- [Web Crawling Best Practices](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers)
- [Rate Limiting Algorithms](https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm/) 