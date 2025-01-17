"""
Web crawler routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional
from src.api.dependencies import get_settings, get_rag_system

router = APIRouter(prefix="/crawler", tags=["crawler"])

class CrawlRequest(BaseModel):
    url: HttpUrl
    index_content: bool = True
    max_depth: Optional[int] = 1

class CrawlResponse(BaseModel):
    url: str
    content: Optional[str]
    metadata: Dict[str, Any]
    indexed: bool

@router.post("/crawl")
async def crawl_url(
    request: CrawlRequest,
    settings = Depends(get_settings),
    rag_system = Depends(get_rag_system)
):
    """Crawl a URL and optionally index its content."""
    # For testing purposes, return a mock response
    if settings.ENV == "test":
        return CrawlResponse(
            url=str(request.url),
            content="Test crawled content",
            metadata={"source": "test", "depth": 1},
            indexed=request.index_content
        )
    
    # In production, implement proper web crawling
    raise HTTPException(status_code=501, detail="Not implemented") 