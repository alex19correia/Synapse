from typing import Generator
from functools import lru_cache

from fastapi import Depends
from supabase import create_client

from .config import get_settings
from .services.document_service import DocumentService
from .services.embedding_service import EmbeddingService

@lru_cache()
def get_supabase_client():
    """Get a cached Supabase client instance."""
    settings = get_settings()
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )

def get_document_service(
    supabase = Depends(get_supabase_client)
) -> DocumentService:
    """Get an instance of the DocumentService."""
    return DocumentService(supabase=supabase)

def get_embedding_service(
    supabase = Depends(get_supabase_client)
) -> EmbeddingService:
    """Get an instance of the EmbeddingService."""
    settings = get_settings()
    return EmbeddingService(
        supabase=supabase,
        openai_api_key=settings.OPENAI_API_KEY
    ) 