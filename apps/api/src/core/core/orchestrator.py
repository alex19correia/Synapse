from typing import Dict, List, Type
from src.core.base_agent import BaseAgent

class AgentOrchestrator:
    """Orquestrador central dos agentes."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, List[str]] = {}
    
    async def route_query(self, query: str, context: dict) -> str:
        """Roteia a query para o agente mais apropriado."""
        agent_scores = await self._score_agents_for_query(query)
        best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]
        return await self.agents[best_agent].process(query, context)
    
    async def execute_workflow(self, workflow_name: str, input_data: dict) -> dict:
        """Executa um workflow predefinido de múltiplos agentes."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow {workflow_name} não encontrado")
            
        result = input_data
        for agent_name in self.workflows[workflow_name]:
            agent = self.agents[agent_name]
            result = await agent.process(result)
        
        return result
    
    def register_workflow(self, name: str, agent_sequence: List[str]):
        """Registra um novo workflow de agentes."""
        self.workflows[name] = agent_sequence 