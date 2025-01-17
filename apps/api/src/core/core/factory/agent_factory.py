import uuid
from typing import Optional, Dict
from src.core.templates.base_agent import BaseSpecializedAgent, AgentConfig
from src.core.registry import AgentRegistry
from src.core.monitoring import MonitoringIntegration
from src.core.memory import MemoryManager

class AgentFactory:
    """Factory para criação de novos agentes."""
    
    def __init__(
        self,
        registry: AgentRegistry,
        memory: Optional[MemoryManager] = None,
        monitoring: Optional[MonitoringIntegration] = None
    ):
        self.registry = registry
        self.memory = memory
        self.monitoring = monitoring
    
    async def create_agent(
        self,
        agent_type: str,
        config: Optional[Dict] = None
    ) -> BaseSpecializedAgent:
        """Cria nova instância de agente."""
        agent_class = await self.registry.get_agent(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_config = AgentConfig(
            agent_id=f"{agent_type}-{uuid.uuid4().hex[:8]}",
            version="1.0.0",
            capabilities=[agent_type],
            **(config or {})
        )
        
        return agent_class(
            config=agent_config,
            memory=self.memory,
            monitoring=self.monitoring
        ) 