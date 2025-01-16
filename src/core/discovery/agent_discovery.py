from typing import List, Dict
from src.core.registry import AgentRegistry
from src.core.monitoring import MonitoringIntegration

class AgentDiscovery:
    """Sistema de descoberta e análise de agentes."""
    
    def __init__(
        self,
        registry: AgentRegistry,
        monitoring: MonitoringIntegration
    ):
        self.registry = registry
        self.monitoring = monitoring
    
    async def discover_capabilities(self) -> Dict[str, List[str]]:
        """Descobre capacidades disponíveis no sistema."""
        agents = await self.registry.list_agents()
        capabilities = {}
        
        for agent_id, config in agents.items():
            for capability in config.capabilities:
                if capability not in capabilities:
                    capabilities[capability] = []
                capabilities[capability].append(agent_id)
        
        return capabilities
    
    async def analyze_requirements(self, requirements: List[str]) -> List[str]:
        """Analisa requisitos e sugere agentes necessários."""
        capabilities = await self.discover_capabilities()
        needed_agents = set()
        
        for requirement in requirements:
            if requirement in capabilities:
                needed_agents.update(capabilities[requirement])
        
        return list(needed_agents) 