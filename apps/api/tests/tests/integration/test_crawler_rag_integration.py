import pytest
import asyncio
from typing import List
import aiohttp
from src.crawlers.parallel_crawler import ParallelCrawler
from src.crawlers.config import CrawlerConfig
from src.crawlers.rag_integration import RAGProcessor

# URLs de teste reais (sites estáticos para evitar mudanças frequentes)
TEST_URLS = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpstat.us/200"
]

@pytest.fixture
async def http_session():
    """Fixture para sessão HTTP compartilhada"""
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.fixture
def crawler_config():
    """Fixture para configuração do crawler"""
    return CrawlerConfig(
        max_concurrent=2,
        batch_size=2,
        browser_settings={
            "headless": True,
            "timeout": 30000
        },
        extraction_settings={
            "use_llm": True,
            "max_retries": 2
        }
    )

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_crawl_and_rag_flow(crawler_config):
    """Testa o fluxo completo de crawling e processamento RAG"""
    
    # Inicializa componentes
    rag_processor = RAGProcessor(
        chunk_size=256,  # Menor para teste
        chunk_overlap=25,
        batch_size=2
    )
    
    crawler = ParallelCrawler(
        max_concurrent=crawler_config.max_concurrent,
        batch_size=crawler_config.batch_size,
        rag_processor=rag_processor
    )
    
    try:
        # Executa crawling com processamento RAG
        result = await crawler.crawl_urls(TEST_URLS, process_rag=True)
        
        # Verifica estrutura básica do resultado
        assert "content" in result
        assert "metrics" in result
        assert isinstance(result["content"], list)
        
        # Verifica conteúdo crawleado
        content = result["content"]
        assert len(content) > 0
        
        for item in content:
            assert item.title
            assert item.content
            assert item.url in TEST_URLS
            assert isinstance(item.metadata, dict)
        
        # Verifica métricas de crawling
        crawl_metrics = result["metrics"]["crawl"]
        assert crawl_metrics["total_urls"] == len(TEST_URLS)
        assert crawl_metrics["success"] > 0
        
        # Verifica métricas RAG
        rag_metrics = result["metrics"]["rag"]
        assert rag_metrics is not None
        assert rag_metrics["total_documents"] > 0
        assert rag_metrics["chunks_generated"] > 0
        assert rag_metrics["embeddings_generated"] > 0
        assert rag_metrics["vectors_stored"] > 0
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {str(e)}")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl_with_invalid_urls(crawler_config):
    """Testa comportamento com URLs inválidas"""
    invalid_urls = [
        "https://invalid.example.com",
        "https://httpstat.us/404",
        "https://httpstat.us/500"
    ]
    
    crawler = ParallelCrawler(
        max_concurrent=crawler_config.max_concurrent,
        batch_size=crawler_config.batch_size
    )
    
    result = await crawler.crawl_urls(invalid_urls, process_rag=True)
    
    # Verifica que erros foram registrados
    assert result["metrics"]["crawl"]["errors"] > 0
    
    # Verifica que RAG não foi processado (sem conteúdo válido)
    assert result["metrics"]["rag"] is None
    assert len(result["content"]) == 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_crawling_performance(crawler_config):
    """Testa performance do crawling paralelo"""
    # Gera lista maior de URLs
    urls = TEST_URLS * 3  # 9 URLs no total
    
    # Testa com diferentes níveis de paralelismo
    async def run_with_concurrency(concurrency: int) -> float:
        crawler = ParallelCrawler(
            max_concurrent=concurrency,
            batch_size=concurrency,
            rag_processor=None  # Desativa RAG para focar no crawling
        )
        
        start_time = asyncio.get_event_loop().time()
        result = await crawler.crawl_urls(urls, process_rag=False)
        duration = asyncio.get_event_loop().time() - start_time
        
        return duration
    
    # Testa com diferentes níveis de paralelismo
    durations = []
    for concurrency in [1, 2, 3]:
        duration = await run_with_concurrency(concurrency)
        durations.append(duration)
    
    # Verifica se maior paralelismo resulta em menor tempo
    assert durations[0] > durations[1], "Paralelismo não melhorou performance"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_rate_limiting_behavior(crawler_config):
    """Testa comportamento do rate limiting"""
    # Configura rate limit baixo
    crawler_config.rate_limit["requests_per_second"] = 1
    
    crawler = ParallelCrawler(
        max_concurrent=2,
        batch_size=2
    )
    
    start_time = asyncio.get_event_loop().time()
    result = await crawler.crawl_urls(TEST_URLS, process_rag=False)
    duration = asyncio.get_event_loop().time() - start_time
    
    # Com rate limit de 1 req/s, deve demorar pelo menos N segundos
    min_expected_duration = len(TEST_URLS) - 1  # -1 porque primeira request é imediata
    assert duration >= min_expected_duration, "Rate limiting não está funcionando" 