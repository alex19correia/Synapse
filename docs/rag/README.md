# RAG System Documentation

## Overview
The RAG (Retrieval-Augmented Generation) system provides document processing, embedding generation, and similarity search capabilities. The system supports multi-vector retrieval, combining different embedding types for more accurate results.

## Core Components

### 1. Multi-Vector Processing (`packages/core/src/memory/memory/enhanced_rag.py`)
- Generates multiple embeddings per document:
  - Semantic embeddings (OpenAI)
  - Keyword-based embeddings (TF-IDF)
  - Code-specific embeddings
- Configurable weights for different embedding types
- Smart combination of search results

### 2. Vector Storage (Supabase)
- Stores multiple embeddings per document
- Efficient similarity search using pgvector
- Rich metadata support
- Automatic indexing for each embedding type

## Database Schema

### Enhanced Documents Table
```sql
CREATE TABLE enhanced_documents (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    embeddings JSONB NOT NULL,  -- Stores multiple embeddings
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

### Indexes
- Semantic embedding index (IVFFlat)
- Keyword embedding index (IVFFlat)
- Code embedding index (IVFFlat)

## Usage Examples

### 1. Basic Document Processing
```python
from src.memory.memory.enhanced_rag import EnhancedRAGSystem, EmbeddingType
from src.config.settings import Settings

# Initialize
settings = Settings()
rag = EnhancedRAGSystem(settings)

# Process document with all embedding types
await rag.process_and_store_document(
    content="Your document content",
    metadata={"type": "documentation"}
)

# Process with specific embedding types
await rag.process_and_store_document(
    content="def example(): return True",
    metadata={"type": "code", "language": "python"},
    embedding_types=[EmbeddingType.SEMANTIC, EmbeddingType.CODE]
)
```

### 2. Multi-Vector Retrieval
```python
# Default retrieval (uses all embedding types)
results = await rag.retrieve_relevant_documentation(
    query="How to implement RAG?",
    limit=5
)

# Custom weights for different embedding types
results = await rag.retrieve_relevant_documentation(
    query="def process_document",
    weights={
        EmbeddingType.SEMANTIC: 0.3,
        EmbeddingType.CODE: 0.7
    }
)

# Access combined results
for result in results:
    print(f"Content: {result.content}")
    print(f"Combined Score: {result.combined_score}")
    print(f"Individual Scores: {result.scores}")
```

## Configuration

### Embedding Types
```python
class EmbeddingType(Enum):
    SEMANTIC = "semantic"  # OpenAI embeddings
    KEYWORD = "keyword"    # TF-IDF vectors
    CODE = "code"         # Code-specific embeddings
```

### Default Weights
- Semantic: 0.6 (General understanding)
- Keyword: 0.3 (Term matching)
- Code: 0.1 (Code patterns)

## Best Practices

1. **Document Processing**
   - Include relevant metadata for better filtering
   - Choose appropriate embedding types for content
   - Consider document length for chunking

2. **Retrieval**
   - Adjust weights based on query type
   - Use appropriate similarity thresholds
   - Consider result diversity

3. **Performance**
   - Use batch processing for multiple documents
   - Monitor embedding generation costs
   - Leverage caching when possible

## Error Handling
The system includes comprehensive error handling:
- Embedding generation retries
- Database connection error handling
- Invalid input validation
- Rate limit management

## Monitoring
Monitor key metrics:
- Embedding generation time
- Search latency
- Result quality scores
- Cache hit rates

## Integration Points
- API Routes: Use EnhancedRAGSystem for document operations
- LLM Integration: Use retrieve_relevant_documentation for context
- Monitoring: Built-in error logging and metrics