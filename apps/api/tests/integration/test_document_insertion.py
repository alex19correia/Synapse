"""Integration tests for document insertion."""
import pytest
from loguru import logger
from src.config.settings import get_settings
from packages.core.src.memory.memory.enhanced_rag import EnhancedRAGSystem

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def rag_system():
    """Get RAG system instance."""
    settings = get_settings()
    return EnhancedRAGSystem(settings)

# Sample test documents
TEST_DOCUMENTS = [
    {
        "content": """
        def process_embeddings(vectors: List[np.ndarray]) -> np.ndarray:
            '''Process and normalize embedding vectors.'''
            return np.mean(vectors, axis=0)
        """,
        "metadata": {
            "type": "code",
            "language": "python",
            "category": "vector_processing"
        }
    },
    {
        "content": """
        Vector embeddings are numerical representations of data that capture semantic meaning.
        They enable similarity search and clustering by converting text into high-dimensional vectors.
        """,
        "metadata": {
            "type": "documentation",
            "category": "embeddings",
            "format": "markdown"
        }
    },
    {
        "content": """
        SELECT 1 - (embeddings->>'semantic')::vector <=> query_embedding AS similarity
        FROM documents
        WHERE similarity > 0.8
        ORDER BY similarity DESC;
        """,
        "metadata": {
            "type": "code",
            "language": "sql",
            "category": "vector_search"
        }
    }
]

async def test_batch_document_insertion(rag_system):
    """Test inserting multiple documents with different types."""
    logger.info("Testing batch document insertion...")
    
    try:
        # Insert documents
        for i, doc in enumerate(TEST_DOCUMENTS, 1):
            logger.info(f"\nProcessing document {i}/{len(TEST_DOCUMENTS)}...")
            logger.info(f"Type: {doc['metadata']['type']}")
            
            success = await rag_system.process_and_store_document(
                content=doc["content"],
                metadata=doc["metadata"]
            )
            
            assert success, f"Failed to store document {i}"
            logger.info(f"✅ Document {i} stored successfully")
        
        # Verify retrieval
        logger.info("\nVerifying document retrieval...")
        
        # Test code search
        code_results = await rag_system.retrieve_relevant_documentation(
            query="vector processing function python",
            limit=1
        )
        assert len(code_results) > 0
        assert code_results[0].metadata["type"] == "code"
        logger.info("✅ Code document retrieved successfully")
        
        # Test documentation search
        doc_results = await rag_system.retrieve_relevant_documentation(
            query="what are vector embeddings",
            limit=1
        )
        assert len(doc_results) > 0
        assert doc_results[0].metadata["type"] == "documentation"
        logger.info("✅ Documentation retrieved successfully")
        
        # Test SQL search
        sql_results = await rag_system.retrieve_relevant_documentation(
            query="postgres vector similarity search",
            limit=1
        )
        assert len(sql_results) > 0
        assert sql_results[0].metadata["language"] == "sql"
        logger.info("✅ SQL document retrieved successfully")
        
        logger.info("✨ All documents processed and verified successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise 