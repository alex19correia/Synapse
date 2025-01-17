from typing import Dict, Type, Optional
from src.core.templates.base_agent import BaseSpecializedAgent, AgentConfig

class AgentRegistry:
    """Registro central de agentes disponíveis."""
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseSpecializedAgent]] = {}
        self._configs: Dict[str, AgentConfig] = {}
        self._instances: Dict[str, BaseSpecializedAgent] = {}
    
    async def register(
        self,
        agent_class: Type[BaseSpecializedAgent],
        config: AgentConfig
    ):
        """Registra um novo tipo de agente."""
        if config.agent_id in self._agents:
            raise ValueError(f"Agent {config.agent_id} already registered")
            
        self._agents[config.agent_id] = agent_class
        self._configs[config.agent_id] = config
    
    async def get_agent(self, agent_id: str) -> Optional[BaseSpecializedAgent]:
        """Recupera ou cria instância do agente."""
        if agent_id not in self._instances:
            if agent_id not in self._agents:
                return None
                
            agent_class = self._agents[agent_id]
            config = self._configs[agent_id]
            self._instances[agent_id] = agent_class(config)
            
        return self._instances[agent_id]
    
    async def list_agents(self) -> Dict[str, AgentConfig]:
        """Lista todos os agentes registrados."""
        return self._configs.copy() 