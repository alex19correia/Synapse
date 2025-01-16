import pytest
from src.services.rag_service import RAGService
from src.config.llm_config import LLMConfig

@pytest.mark.asyncio
async def test_rag_service_init():
    """Testa inicialização do RAG Service"""
    config = LLMConfig()
    service = RAGService(config)
    assert service is not None
    assert service.config == config
    assert service.embeddings is not None
    assert service.vector_store is None

@pytest.mark.asyncio
async def test_rag_service_add_documents():
    """Testa adição de documentos"""
    config = LLMConfig()
    service = RAGService(config)
    
    docs = [
        "Este é um documento de teste",
        "Este é outro documento para testar o sistema"
    ]
    metadata = [
        {"source": "test1.txt"},
        {"source": "test2.txt"}
    ]
    
    await service.add_documents(docs, metadata)
    assert service.vector_store is not None

@pytest.mark.asyncio
async def test_rag_service_query():
    """Testa processamento de query com documentos"""
    config = LLMConfig()
    service = RAGService(config)
    
    # Adiciona documentos
    docs = ["Python é uma linguagem de programação"]
    await service.add_documents(docs)
    
    # Testa query
    result = await service.process_query("O que é Python?")
    assert result is not None
    assert result["type"] == "rag_response"
    assert len(result["sources"]) > 0 