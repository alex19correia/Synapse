"""API dependencies."""
from typing import Annotated, Dict, Set
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
import httpx

from src.config.settings import Settings, get_settings
from src.llm.llm_service import LLMService
from src.rag.rag_system import RAGSystem
from src.database import Database
from src.db.supabase import SupabaseClient

security = HTTPBearer()

# Token blacklist for invalidated tokens
token_blacklist: Set[str] = set()

@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

def get_db() -> Database:
    """Get database instance."""
    return Database()

def get_llm_client() -> LLMService:
    """Get LLM client instance."""
    settings = get_settings()
    return LLMService(settings)

async def get_rag_system() -> RAGSystem:
    """Get RAG system instance."""
    rag = RAGSystem(get_settings())
    await rag.initialize()
    return rag

def get_supabase_client() -> SupabaseClient:
    """Get Supabase client."""
    settings = get_settings()
    return SupabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def invalidate_token(token: str) -> None:
    """Add token to blacklist."""
    token_blacklist.add(token)

async def verify_clerk_token(token: str, settings: Settings) -> Dict[str, str]:
    """Verify Clerk token.
    
    Args:
        token: JWT token
        settings: Application settings
        
    Returns:
        User info
        
    Raises:
        HTTPException: If token is invalid
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.clerk.dev/v1/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        data = response.json()
        return {
            "id": data["id"],
            "email": data["email_addresses"][0]["email_address"],
            "name": f"{data['first_name']} {data['last_name']}"
        }

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Get current authenticated user."""
    # Allow test routes without auth
    if request.url.path.startswith("/api/test"):
        return {
            "id": "test-user",
            "email": "test@example.com",
            "name": "Test User"
        }

    # Check if token is blacklisted
    if credentials.credentials in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # For testing purposes, validate test tokens
    if settings.ENV == "test":
        if credentials.credentials == "test-token":
            return {
                "id": "test-user",
                "email": "test@example.com",
                "name": "Test User"
            }

    # Verify token with Clerk
    return await verify_clerk_token(credentials.credentials, settings)

# Dependency types
RAGDep = Annotated[RAGSystem, Depends(get_rag_system)]
LLMDep = Annotated[LLMService, Depends(get_llm_client)]
DBDep = Annotated[Database, Depends(get_db)]
SupabaseDep = Annotated[SupabaseClient, Depends(get_supabase_client)]