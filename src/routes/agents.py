from fastapi import APIRouter, Depends
from src.agents.web_researcher.agent import WebResearcherAgent
from src.agents.web_researcher.config import WebResearcherConfig

router = APIRouter()

@router.post("/web-research")
async def web_research(
    query: str,
    config: WebResearcherConfig = Depends()
):
    agent = WebResearcherAgent()
    result = await agent.search_web(query, config.brave_api_key)
    return {"result": result} 