from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.agents.web_researcher.agent import WebResearcherAgent
from src.config import get_settings

router = APIRouter(prefix="/web-researcher", tags=["web-researcher"])

class WebSearchRequest(BaseModel):
    query: str

@router.post("/search")
async def web_search(request: WebSearchRequest):
    """
    Realiza uma pesquisa na web usando o Web Researcher Agent.
    """
    settings = get_settings()
    agent = WebResearcherAgent()
    
    try:
        result = await agent.search_web(
            query=request.query,
            brave_api_key=settings.brave_api_key
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 