import pytest
from src.agents.github_assistant import GitHubAssistant
from src.utils.nlp_extractor import GitHubEntity

@pytest.mark.asyncio
async def test_github_assistant_init():
    """Testa inicialização do GitHub Assistant"""
    assistant = GitHubAssistant()
    assert assistant is not None

@pytest.mark.asyncio
async def test_process_simple_query():
    """Testa processamento de query simples"""
    assistant = GitHubAssistant()
    query = "Mostre o arquivo README.md"
    
    # Simula extração de entidades
    entities = [
        GitHubEntity(type="file_path", value="README.md", confidence=0.9)
    ]
    
    result = await assistant.process_query(query, {"entities": entities})
    assert result is not None
    assert "content" in result 