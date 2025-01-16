from typing import List, Dict
from src.core.orchestrator import AgentOrchestrator
from src.core.memory import MemoryManager
from src.core.analytics import AnalyticsTracker

class BasicWorkflow:
    """Implementação de workflows básicos."""
    
    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        memory: MemoryManager,
        analytics: AnalyticsTracker
    ):
        self.orchestrator = orchestrator
        self.memory = memory
        self.analytics = analytics
    
    async def tech_analysis(self, query: str, context: Dict) -> Dict:
        """Workflow de análise técnica."""
        # 1. Pesquisa inicial
        research = await self.orchestrator.execute_agent(
            "web_researcher",
            query,
            context
        )
        
        # 2. Análise técnica
        tech_analysis = await self.orchestrator.execute_agent(
            "tech_stack_expert",
            query,
            {**context, "research": research}
        )
        
        # 3. Verificação de repos similares
        similar_repos = await self.orchestrator.execute_agent(
            "github_assistant",
            query,
            {**context, "tech_stack": tech_analysis}
        )
        
        return {
            "research": research,
            "tech_analysis": tech_analysis,
            "similar_repos": similar_repos
        } 