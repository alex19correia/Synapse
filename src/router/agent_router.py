from typing import Dict, List, Optional
from pydantic import BaseModel
from ..agents.base_agent import BaseAgent
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AgentRouter(BaseModel):
    agents: List[BaseAgent]
    fallback_threshold: float = 0.3

    class Config:
        arbitrary_types_allowed = True

    async def route_query(self, query: str, context: Dict) -> Optional[BaseAgent]:
        """
        Determina qual agente deve processar a query baseado em scores de confiança.
        
        Args:
            query: Input do usuário
            context: Contexto da conversa
            
        Returns:
            Agente mais apropriado ou None
        """
        best_agent = None
        best_score = self.fallback_threshold

        for agent in self.agents:
            try:
                score = await agent.can_handle(query, context)
                logger.debug(f"Agent {agent.name} confidence: {score}")
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            except Exception as e:
                logger.error(f"Error checking agent {agent.name}: {e}")
                continue

        return best_agent 