import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import json
from src.agents.web_researcher.agent import WebResearcherAgent

@pytest.fixture
def mock_env_vars():
    """Fixture para configurar variáveis de ambiente para testes."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key',
        'LLM_MODEL': 'gpt-3.5-turbo',
        'BRAVE_API_KEY': 'test-brave-key'
    }):
        yield

@pytest.fixture
def mock_agent():
    """Mock para o Agent."""
    async def mock_run(*args, **kwargs):
        return MagicMock(data="Mocked Agent Response")
    
    with patch('pydantic_ai.Agent.run', new=mock_run):
        yield

@pytest.mark.asyncio
async def test_web_researcher_with_mock_brave(mock_env_vars, mock_agent):
    """Testa a integração com a API do Brave usando mock."""
    mock_data = {
        "web": {
            "results": [
                {
                    "title": "Test Article 1",
                    "description": "Description 1",
                    "url": "https://test1.com"
                }
            ]
        }
    }

    class MockResponse:
        async def aread(self):
            return json.dumps(mock_data).encode()
        
        async def raise_for_status(self):
            return None
        
        def json(self):
            return mock_data

    with patch('httpx.AsyncClient.get', return_value=MockResponse()):
        agent = WebResearcherAgent(use_cache=False)
        result = await agent.search_web(
            "Test query with mock",
            brave_api_key="test_key"
        )
        assert isinstance(result, str)
        assert "Test Article 1" in result or "Mocked Agent Response" in result

@pytest.mark.asyncio
async def test_web_researcher_empty_results(mock_env_vars, mock_agent):
    """Testa o comportamento quando não há resultados."""
    mock_data = {"web": {"results": []}}

    class MockResponse:
        async def aread(self):
            return json.dumps(mock_data).encode()
        
        async def raise_for_status(self):
            return None
        
        def json(self):
            return mock_data

    with patch('httpx.AsyncClient.get', return_value=MockResponse()):
        agent = WebResearcherAgent(use_cache=False)
        result = await agent.search_web(
            "Query without results",
            brave_api_key="test_key"
        )
        assert isinstance(result, str)
        assert "No results found" in result or "Mocked Agent Response" in result

@pytest.mark.asyncio
async def test_web_researcher_search(mock_env_vars, mock_agent):
    """Testa a funcionalidade básica do Web Researcher."""
    agent = WebResearcherAgent(use_cache=False)
    result = await agent.search_web(
        "What are the latest developments in AI?",
        brave_api_key="test_key"
    )
    assert result is not None
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_web_researcher_no_brave_key(mock_env_vars, mock_agent):
    """Testa o comportamento quando não há chave Brave."""
    agent = WebResearcherAgent(use_cache=False)
    result = await agent.search_web(
        "Test query",
        brave_api_key=None
    )
    assert "test web search result" in result.lower()

@pytest.mark.asyncio
async def test_web_researcher_api_error(mock_env_vars, mock_agent):
    """Testa o comportamento em caso de erro na API."""
    with patch('httpx.AsyncClient.get', side_effect=Exception("API Error")):
        agent = WebResearcherAgent(use_cache=False)
        result = await agent.search_web(
            "Test query with error",
            brave_api_key="test_key"
        )
        assert "Error processing query" in result 