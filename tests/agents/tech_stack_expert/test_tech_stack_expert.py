import pytest
from unittest.mock import AsyncMock, patch
from src.agents.tech_stack_expert.agent import TechStackExpertAgent
from src.agents.tech_stack_expert.models import TechStackRequirements

@pytest.fixture
def mock_memory():
    return AsyncMock()

@pytest.fixture
def agent(mock_memory):
    return TechStackExpertAgent(memory=mock_memory)

@pytest.mark.asyncio
async def test_initial_conversation(agent):
    """Testa o início da conversação."""
    response = await agent.analyze_requirements("Olá, preciso de ajuda com minha stack")
    assert "descreva a aplicação" in response.lower()

@pytest.mark.asyncio
async def test_recommendation_generation(agent):
    """Testa a geração de recomendações."""
    requirements = TechStackRequirements(
        app_description="App de IA com RAG",
        ai_coding_assistant="Cursor",
        frontend_experience=["React", "Vue"],
        backend_experience=["Python", "FastAPI"],
        user_scale="100-1,000",
        specific_requirements={"database": "PostgreSQL"}
    )
    
    recommendation = await agent.recommend_stack(requirements)
    assert recommendation.frontend is not None
    assert recommendation.backend is not None
    assert recommendation.database is not None 