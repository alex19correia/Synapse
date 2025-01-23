"""Integration tests for vector search functionality."""
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

async def test_vector_search_flow(rag_system):
    """Test complete vector search flow."""
    logger.info("Testing vector search functionality...")
    
    # Test document
    test_doc = {
        "content": """
        def calculate_similarity(vec1, vec2):
            return 1 - cosine_distance(vec1, vec2)
        """,
        "metadata": {
            "type": "code",
            "language": "python",
            "description": "Similarity calculation function"
        }
    }
    
    try:
        # 1. Store document
        logger.info("Storing test document...")
        success = await rag_system.process_and_store_document(
            content=test_doc["content"],
            metadata=test_doc["metadata"]
        )
        assert success, "Failed to store document"
        logger.info("✅ Document stored successfully")
        
        # 2. Search with different embedding types
        logger.info("Testing search with different embedding types...")
        
        # Semantic search
        semantic_results = await rag_system.retrieve_relevant_documentation(
            query="How to calculate vector similarity?",
            embedding_types=[EmbeddingType.SEMANTIC]
        )
        assert len(semantic_results) > 0, "No semantic results found"
        logger.info(f"✅ Semantic search returned {len(semantic_results)} results")
        
        # Code search
        code_results = await rag_system.retrieve_relevant_documentation(
            query="function cosine_distance python",
            embedding_types=[EmbeddingType.CODE]
        )
        assert len(code_results) > 0, "No code results found"
        logger.info(f"✅ Code search returned {len(code_results)} results")
        
        # Combined search
        combined_results = await rag_system.retrieve_relevant_documentation(
            query="similarity function implementation",
            weights={
                EmbeddingType.SEMANTIC: 0.4,
                EmbeddingType.CODE: 0.6
            }
        )
        assert len(combined_results) > 0, "No combined results found"
        logger.info(f"✅ Combined search returned {len(combined_results)} results")
        
        # 3. Verify result scores
        result = combined_results[0]
        assert result.scores[EmbeddingType.SEMANTIC] >= 0
        assert result.scores[EmbeddingType.CODE] >= 0
        assert 0 <= result.combined_score <= 1
        logger.info("✅ Result scores verified")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
        
    logger.info("✨ Vector search test completed successfully") 