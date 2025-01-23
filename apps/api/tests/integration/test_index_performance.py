"""Integration tests for vector index performance."""
import pytest
from loguru import logger
from src.config.settings import get_settings
from packages.core.src.memory.memory.enhanced_rag import EnhancedRAGSystem, EmbeddingType

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def rag_system():
    """Get RAG system instance."""
    settings = get_settings()
    return EnhancedRAGSystem(settings)

async def test_index_performance(rag_system):
    """Test vector index performance."""
    logger.info("Testing index performance...")
    
    try:
        # 1. Get index statistics
        logger.info("Getting index statistics...")
        stats = await rag_system.get_index_stats()
        
        for index_name, index_stats in stats.items():
            logger.info(f"\nIndex: {index_name}")
            logger.info(f"Total scans: {index_stats.total_scans}")
            logger.info(f"Average scan time: {index_stats.avg_scan_time}ms")
            logger.info(f"Size: {index_stats.size_bytes / 1024:.2f}KB")
            logger.info(f"Last vacuum: {index_stats.last_vacuum}")
        
        # 2. Analyze query performance
        logger.info("\nAnalyzing query performance...")
        query = "function implementation"
        
        for embedding_type in EmbeddingType:
            logger.info(f"\nTesting {embedding_type.value} index...")
            performance = await rag_system.analyze_query_performance(
                query=query,
                embedding_type=embedding_type
            )
            
            if performance:
                logger.info(f"Estimated cost: {performance.get('estimated_cost', 'N/A')}")
                logger.info(f"Actual time: {performance.get('actual_time', 'N/A')}ms")
                logger.info(f"Query plan: {performance.get('query_plan', 'N/A')}")
        
        logger.info("✨ Performance analysis completed")
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        raise 