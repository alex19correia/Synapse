import asyncio
from typing import List

# Imports relativos ao pacote src
from src.crawlers.parallel_crawler import ParallelCrawler
from src.crawlers.config import CrawlerConfig
from src.lib.logger import logger

async def main():
    # Configuração personalizada
    config = CrawlerConfig(
        max_concurrent=5,
        batch_size=10,
        browser_settings={
            "headless": True,
            "timeout": 30000
        },
        extraction_settings={
            "use_llm": True,
            "max_retries": 3
        }
    )
    
    # URLs de exemplo
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        # ... mais URLs
    ]
    
    try:
        # Inicializa o crawler
        crawler = ParallelCrawler(
            max_concurrent=config.max_concurrent,
            batch_size=config.batch_size
        )
        
        # Executa o crawling e processamento RAG
        logger.info(f"Starting crawl of {len(urls)} URLs...")
        result = await crawler.crawl_urls(urls, process_rag=True)
        
        # Analisa resultados
        crawl_metrics = result["metrics"]["crawl"]
        rag_metrics = result["metrics"]["rag"]
        
        logger.info("Crawling completed:")
        logger.info(f"- Total URLs: {crawl_metrics['total_urls']}")
        logger.info(f"- Successful: {crawl_metrics['success']}")
        logger.info(f"- Errors: {crawl_metrics['errors']}")
        
        if rag_metrics:
            logger.info("\nRAG Processing completed:")
            logger.info(f"- Documents processed: {rag_metrics['total_documents']}")
            logger.info(f"- Chunks generated: {rag_metrics['chunks_generated']}")
            logger.info(f"- Embeddings generated: {rag_metrics['embeddings_generated']}")
            logger.info(f"- Vectors stored: {rag_metrics['vectors_stored']}")
        
        # Acessa o conteúdo extraído
        contents = result["content"]
        logger.info(f"\nExtracted {len(contents)} documents")
        
        # Exemplo de acesso ao primeiro documento
        if contents:
            first_doc = contents[0]
            logger.info("\nFirst document:")
            logger.info(f"- Title: {first_doc.title}")
            logger.info(f"- URL: {first_doc.url}")
            logger.info(f"- Content length: {len(first_doc.content)}")
            logger.info(f"- Metadata: {first_doc.metadata}")
        
    except Exception as e:
        logger.error(f"Error in crawler example: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 