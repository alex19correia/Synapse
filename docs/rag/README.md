# Sistema RAG (Retrieval-Augmented Generation) 🔍

## Visão Geral

O sistema RAG do Synapse Assistant implementa um pipeline completo de recuperação e geração aumentada, permitindo respostas precisas e contextualizadas baseadas em documentos e conhecimento armazenado.

## Componentes

### 1. Document Processor
```python
from src.rag.processor import DocumentProcessor

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
        
    async def process(self, document: Document) -> list[Chunk]:
        # Extract text
        text = await self.extract_text(document)
        
        # Split into chunks
        chunks = self.split_text(text)
        
        # Process metadata
        chunks = [self.add_metadata(chunk, document) for chunk in chunks]
        
        return chunks
```

### 2. Vector Store
```python
from src.rag.vector_store import VectorStore

class VectorStore:
    def __init__(self, client: QdrantClient):
        self.client = client
        
    async def add_documents(self, chunks: list[Chunk]):
        # Get embeddings
        embeddings = await self.get_embeddings(chunks)
        
        # Store vectors
        await self.client.upload_vectors(
            collection="documents",
            vectors=embeddings,
            metadata=[chunk.metadata for chunk in chunks]
        )
```

## Pipeline

### 1. Indexing Pipeline
```python
class IndexingPipeline:
    async def process_document(self, document: Document):
        # Process document
        chunks = await self.processor.process(document)
        
        # Get embeddings
        embeddings = await self.embedder.embed_chunks(chunks)
        
        # Store in vector database
        await self.vector_store.add_documents(chunks, embeddings)
        
        # Index metadata
        await self.metadata_store.index(document.metadata)
```

### 2. Query Pipeline
```python
class QueryPipeline:
    async def query(self, question: str) -> Answer:
        # Get question embedding
        q_embedding = await self.embedder.embed_text(question)
        
        # Retrieve relevant chunks
        chunks = await self.vector_store.search(
            embedding=q_embedding,
            k=5
        )
        
        # Generate answer
        answer = await self.llm.generate_answer(
            question=question,
            context=chunks
        )
        
        return Answer(
            content=answer,
            sources=chunks
        )
```

## Embeddings

### 1. Text Embedder
```python
class TextEmbedder:
    def __init__(self, model: str = "deepseek-embed"):
        self.model = model
        
    async def embed_text(self, text: str) -> Vector:
        embedding = await self.client.embed(text)
        return embedding
    
    async def embed_batch(self, texts: list[str]) -> list[Vector]:
        embeddings = await self.client.embed_batch(texts)
        return embeddings
```

### 2. Chunk Embedder
```python
class ChunkEmbedder:
    async def embed_chunk(self, chunk: Chunk) -> Vector:
        # Prepare text
        text = self.prepare_chunk_text(chunk)
        
        # Get embedding
        embedding = await self.embedder.embed_text(text)
        
        return embedding
```

## Chunking

### 1. Text Splitter
```python
class TextSplitter:
    def split_text(self, text: str) -> list[str]:
        # Split by sentences
        sentences = self.split_sentences(text)
        
        # Combine into chunks
        chunks = self.combine_sentences(
            sentences,
            max_tokens=500,
            overlap=50
        )
        
        return chunks
```

### 2. Chunk Manager
```python
class ChunkManager:
    def process_chunk(self, chunk: str, metadata: dict) -> Chunk:
        return Chunk(
            text=chunk,
            metadata=metadata,
            embedding=None  # Will be added later
        )
```

## Recuperação

### 1. Vector Search
```python
class VectorSearch:
    async def search(self, query: str, k: int = 5) -> list[Document]:
        # Get query embedding
        q_embedding = await self.embedder.embed_text(query)
        
        # Search vector store
        results = await self.vector_store.search(
            embedding=q_embedding,
            k=k
        )
        
        return results
```

### 2. Hybrid Search
```python
class HybridSearch:
    async def search(self, query: str) -> list[Document]:
        # Vector search
        vector_results = await self.vector_search(query)
        
        # Keyword search
        keyword_results = await self.keyword_search(query)
        
        # Combine results
        combined = self.combine_results(
            vector_results,
            keyword_results
        )
        
        return combined
```

## Geração

### 1. Answer Generator
```python
class AnswerGenerator:
    async def generate_answer(self, 
                            question: str,
                            context: list[str]) -> str:
        # Format prompt
        prompt = self.format_prompt(question, context)
        
        # Generate answer
        answer = await self.llm.generate(prompt)
        
        return answer
```

### 2. Context Manager
```python
class ContextManager:
    def prepare_context(self, chunks: list[Chunk]) -> str:
        # Sort by relevance
        sorted_chunks = self.sort_by_relevance(chunks)
        
        # Format context
        context = self.format_chunks(sorted_chunks)
        
        return context
```

## Métricas

### 1. Retrieval Metrics
```python
class RetrievalMetrics:
    async def track_retrieval(self, query: str, results: list[Document]):
        metrics = {
            "query_time": self.measure_time(),
            "num_results": len(results),
            "relevance_scores": self.get_relevance_scores(results)
        }
        await self.save_metrics(metrics)
```

### 2. Generation Metrics
```python
class GenerationMetrics:
    async def track_generation(self, 
                             question: str,
                             answer: str,
                             context: list[str]):
        metrics = {
            "generation_time": self.measure_time(),
            "answer_length": len(answer),
            "context_used": len(context)
        }
        await self.save_metrics(metrics)
```

## Monitoramento

### 1. Quality Monitor
```python
class QualityMonitor:
    async def monitor_quality(self, 
                            question: str,
                            answer: str,
                            feedback: dict):
        # Track metrics
        await self.track_metrics(question, answer)
        
        # Save feedback
        await self.save_feedback(feedback)
        
        # Update quality score
        await self.update_quality_score()
```

### 2. Performance Monitor
```python
class PerformanceMonitor:
    async def monitor_performance(self, metrics: dict):
        # Track latency
        await self.track_latency(metrics["latency"])
        
        # Monitor resource usage
        await self.track_resources(metrics["resources"])
        
        # Check thresholds
        await self.check_thresholds(metrics)
```

## Manutenção

### 1. Index Maintenance
```python
class IndexMaintenance:
    async def maintain_index(self):
        # Optimize vectors
        await self.optimize_vectors()
        
        # Clean old entries
        await self.clean_old_entries()
        
        # Update metadata
        await self.update_metadata()
```

### 2. Quality Maintenance
```python
class QualityMaintenance:
    async def maintain_quality(self):
        # Review low quality answers
        await self.review_low_quality()
        
        # Update training data
        await self.update_training()
        
        # Retrain models if needed
        await self.retrain_models()
```

## Configuração

### 1. RAG Config
```yaml
rag:
  chunking:
    chunk_size: 500
    overlap: 50
  embedding:
    model: deepseek-embed
    batch_size: 32
  retrieval:
    k: 5
    threshold: 0.8
  generation:
    max_length: 1000
    temperature: 0.7
```

### 2. Model Config
```yaml
models:
  embedder:
    name: deepseek-embed
    dimension: 768
  generator:
    name: deepseek-chat
    context_length: 4096
```

## Referências

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [Sentence Transformers](https://www.sbert.net/) 