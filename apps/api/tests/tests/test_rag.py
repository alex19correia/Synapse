import pytest
from src.services.rag_service import RAGService
from src.utils.logger import get_logger

logger = get_logger("test_rag")

@pytest.fixture
def rag_service():
    """Fixture para o serviço RAG"""
    return RAGService()

def test_process_document(rag_service):
    """Testa o processamento de documentos"""
    document = {
        'text': 'Este é um documento de teste para o sistema RAG.',
        'metadata': {
            'source': 'test',
            'type': 'text'
        }
    }
    
    result = rag_service.process_document(document)
    assert result['success'] is True
    assert len(result['chunks']) > 0
    assert len(result['embeddings']) > 0
    
def test_query_documents(rag_service):
    """Testa a consulta de documentos"""
    query = "Como funciona o sistema RAG?"
    
    result = rag_service.query(query)
    assert result['success'] is True
    assert len(result['relevant_chunks']) > 0
    assert result['answer'] is not None
    
def test_invalid_document(rag_service):
    """Testa o processamento de documento inválido"""
    document = {
        'text': '',  # Texto vazio
        'metadata': {}
    }
    
    result = rag_service.process_document(document)
    assert result['success'] is False
    assert 'error' in result
    
def test_invalid_query(rag_service):
    """Testa consulta inválida"""
    query = ""  # Query vazia
    
    result = rag_service.query(query)
    assert result['success'] is False
    assert 'error' in result 