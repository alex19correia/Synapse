from typing import List, Dict, Any, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config.llm_config import LLMConfig
from src.utils.logger import get_logger

class RAGService:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
    
    async def add_documents(self, documents: List[str], metadata: Optional[List[Dict]] = None) -> None:
        """Adiciona documentos ao vector store"""
        texts = []
        metas = []
        
        # Processa cada documento
        for i, doc in enumerate(documents):
            chunks = self.text_splitter.split_text(doc)
            texts.extend(chunks)
            
            # Adiciona metadata para cada chunk
            if metadata and i < len(metadata):
                metas.extend([metadata[i]] * len(chunks))
            else:
                metas.extend([{}] * len(chunks))
        
        # Cria ou atualiza vector store
        if self.vector_store is None:
            self.vector_store = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metas
            )
        else:
            self.vector_store.add_texts(texts, metadatas=metas)
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Processa uma query usando RAG"""
        try:
            if self.vector_store is None:
                return {
                    "type": "error",
                    "content": "Vector store não inicializado. Adicione documentos primeiro."
                }
            
            # Busca documentos relevantes
            docs = self.vector_store.similarity_search(
                query,
                k=3,
                distance_threshold=self.config.similarity_threshold
            )
            
            # Formata resposta
            sources = []
            for doc in docs:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                })
            
            return {
                "type": "rag_response",
                "content": "Documentos relevantes encontrados",
                "sources": sources
            }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"Erro ao processar query RAG: {str(e)}",
                "error": str(e)
            } 