from typing import Dict, List, Optional
from pydantic import BaseModel

class QueryContext(BaseModel):
    """Contexto da query para roteamento."""
    user_id: str
    session_id: str
    query_type: Optional[str]
    priority: Optional[int] = 1

class RouterConfig(BaseModel):
    """Configuração do sistema de roteamento."""
    default_agent: str
    fallback_chain: List[str]
    priority_rules: Dict[str, int]

class QueryRouter:
    """Sistema de roteamento de queries."""
    
    def __init__(self, config: RouterConfig):
        self.config = config
        self._load_routing_rules()
    
    async def route_query(self, query: str, context: QueryContext) -> str:
        """Roteia a query para o agente mais apropriado."""
        agent = await self._determine_best_agent(query, context)
        return agent
    
    async def _determine_best_agent(self, query: str, context: QueryContext) -> str:
        """Determina o melhor agente baseado na query e contexto."""
        scores = await self._score_agents(query, context)
        return max(scores.items(), key=lambda x: x[1])[0] 