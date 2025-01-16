from src.core.orchestrator import AgentOrchestrator

async def analyze_tech_project(query: str, orchestrator: AgentOrchestrator):
    """Workflow completo de análise técnica."""
    
    # 1. Pesquisa web sobre tecnologias mencionadas
    web_research = await orchestrator.agents["web_researcher"].search(query)
    
    # 2. Analisa stack técnica
    tech_recommendation = await orchestrator.agents["tech_stack_expert"].recommend(
        query, 
        context={"web_research": web_research}
    )
    
    # 3. Verifica repositórios similares
    similar_repos = await orchestrator.agents["github_assistant"].find_similar_projects(
        tech_recommendation
    )
    
    return {
        "research": web_research,
        "recommendation": tech_recommendation,
        "similar_projects": similar_repos
    } 