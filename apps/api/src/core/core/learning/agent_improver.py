from typing import Dict, List
from datetime import datetime, timedelta
from src.core.analytics import AnalyticsSystem
from src.core.memory import MemoryManager

class AgentImprover:
    """Sistema de melhoria contínua dos agentes."""
    
    def __init__(
        self,
        analytics: AnalyticsSystem,
        memory: MemoryManager
    ):
        self.analytics = analytics
        self.memory = memory
    
    async def analyze_performance(self, agent_id: str) -> Dict:
        """Analisa performance e sugere melhorias."""
        # Coleta dados recentes
        recent_metrics = await self.analytics.collect_metrics(
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow()
        )
        
        agent_metrics = recent_metrics.get(agent_id)
        if not agent_metrics:
            return {"status": "no_data"}
        
        # Analisa áreas de melhoria
        improvements = await self._identify_improvements(
            agent_id,
            agent_metrics
        )
        
        # Gera recomendações
        return {
            "current_performance": agent_metrics,
            "suggested_improvements": improvements,
            "priority": self._calculate_priority(improvements)
        }
    
    async def apply_improvements(
        self,
        agent_id: str,
        improvements: List[str]
    ):
        """Aplica melhorias sugeridas."""
        for improvement in improvements:
            await self._apply_single_improvement(agent_id, improvement)
            
        # Atualiza memória do agente
        await self.memory.store(
            f"improvements:{agent_id}",
            {
                "timestamp": datetime.utcnow(),
                "improvements": improvements
            }
        ) 