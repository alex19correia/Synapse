import pytest
import asyncio
from datetime import datetime

from src.services.rag_service import RAGService
from src.services.embedding_service import EmbeddingService
from src.services.document_chunker import DocumentChunker
from src.services.metrics_service import MetricsService
from src.services.cache_service import CacheService
from src.config.llm_config import LLMConfig

class TestRAGIntegration:
    @pytest.fixture
    async def setup_services(self):
        # Configuração inicial
        config = LLMConfig()
        metrics_service = MetricsService()
        chunker = DocumentChunker(max_chunk_size=500, overlap=50)
        embedding_service = EmbeddingService(openai_client=None)  # Necessário configurar
        rag_service = RAGService(config)
        
        return {
            "config": config,
            "metrics": metrics_service,
            "chunker": chunker,
            "embeddings": embedding_service,
            "rag": rag_service
        }

    async def test_full_rag_pipeline(self, setup_services):
        # Arrange
        services = await setup_services
        test_document = """
        O Sistema RAG (Retrieval-Augmented Generation) é uma abordagem que combina 
        recuperação de informações com geração de texto. Este sistema permite que 
        modelos de linguagem acessem informações externas durante a geração de 
        respostas, melhorando assim a precisão e confiabilidade das respostas.
        """
        
        metadata = {
            "doc_id": "test_doc_001",
            "source": "integration_test",
            "created_at": datetime.now().isoformat()
        }

        try:
            # 1. Chunking
            print("\n1. Iniciando chunking do documento...")
            chunks = services["chunker"].chunk_document(test_document, metadata)
            print(f"✅ Documento dividido em {len(chunks)} chunks")

            # 2. Embedding Generation
            print("\n2. Gerando embeddings para os chunks...")
            for chunk in chunks:
                embedding = await services["embeddings"].get_embedding(chunk.text)
                print(f"✅ Embedding gerado para chunk {chunk.chunk_id}")

                # 3. Adding to Knowledge Base
                print(f"\n3. Adicionando chunk {chunk.chunk_id} ao knowledge base...")
                success = await services["rag"].add_to_knowledge_base(
                    chunk.text,
                    chunk.metadata,
                    embedding
                )
                assert success, f"Falha ao adicionar chunk {chunk.chunk_id}"
                print(f"✅ Chunk {chunk.chunk_id} adicionado com sucesso")

            # 4. Test Query
            print("\n4. Testando busca...")
            query = "Como o sistema RAG melhora a precisão das respostas?"
            query_embedding = await services["embeddings"].get_embedding(query)
            results = await services["rag"].search_similar(query_embedding)
            
            print("\nResultados da busca:")
            for idx, result in enumerate(results, 1):
                print(f"\nResultado {idx}:")
                print(f"Score: {result['score']:.4f}")
                print(f"Texto: {result['text'][:100]}...")

            assert len(results) > 0, "Nenhum resultado encontrado"
            print("\n✅ Teste de integração completo!")

        except Exception as e:
            print(f"\n❌ Erro durante o teste: {str(e)}")
            raise

if __name__ == "__main__":
    # Para rodar manualmente:
    # pytest src/tests/integration/test_rag_integration.py -v
    pass 