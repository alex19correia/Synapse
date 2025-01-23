# RAG System Documentation

## Overview
The RAG (Retrieval-Augmented Generation) system provides document processing, embedding generation, and similarity search capabilities.

## Core Components

### 1. RAG System (`rag_system.py`)
- Main orchestrator for RAG functionality
- Handles document retrieval and query processing
- Integrates embeddings and vector storage

### 2. Embedding Generator (`embeddings.py`)
- Generates embeddings for text content
- Supports both single and batch embedding generation
- Configurable embedding dimensions

### 3. Vector Store (`storage.py`)
- Manages document storage and retrieval
- Handles vector similarity search
- Integrates with Supabase for persistence

## Usage
To use the RAG system in your code:

```python
from src.rag.rag.rag_system import RAGSystem

# Initialize
rag = RAGSystem(top_k=2)
await rag.initialize()

# Query
result = await rag.query("your query here")
print(result["response"])
print(result["sources"])
```

## Important Notes
1. The system is already integrated with Supabase for vector storage
2. Embeddings are generated using OpenAI's API
3. Document chunking is handled automatically
4. Test mode provides mock data for development

## Integration Points
- API Routes: Use the RAG system directly in your routes
- Services: Avoid creating duplicate services, use RAG system components
- Testing: Use the provided test utilities in test mode 