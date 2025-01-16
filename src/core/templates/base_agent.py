from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel
from src.core.memory import MemoryManager
from src.core.monitoring import MonitoringIntegration

class AgentConfig(BaseModel):
    """Configuração base para agentes."""
    agent_id: str
    version: str
    capabilities: list[str]
    max_retries: int = 3
    timeout: int = 30
    memory_ttl: int = 3600

class BaseSpecializedAgent(ABC):
    """Template base para criação de novos agentes especializados."""
    
    def __init__(
        self,
        config: AgentConfig,
        memory: Optional[MemoryManager] = None,
        monitoring: Optional[MonitoringIntegration] = None
    ):
        self.config = config
        self.memory = memory or MemoryManager()
        self.monitoring = monitoring or MonitoringIntegration(config.agent_id)
        
    @abstractmethod
    async def process(self, query: str, context: Optional[Dict] = None) -> Any:
        """Método principal de processamento."""
        pass
    
    async def execute(self, query: str, context: Optional[Dict] = None) -> Any:
        """Wrapper para execução segura com monitoramento."""
        async with self.monitoring.track_agent_operation(
            self.config.agent_id,
            "process",
            context
        ):
            try:
                result = await self.process(query, context)
                await self._store_result(query, result, context)
                return result
            except Exception as e:
                await self.monitoring.logger.error(
                    "Agent execution failed",
                    error=e,
                    query=query,
                    context=context
                )
                raise
    
    async def _store_result(self, query: str, result: Any, context: Optional[Dict]):
        """Armazena resultado na memória."""
        if self.memory:
            key = f"{self.config.agent_id}:{hash(query)}"
            await self.memory.store(key, {
                "query": query,
                "result": result,
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }, ttl=self.config.memory_ttl) 