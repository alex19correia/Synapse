from typing import Optional, Dict
from datetime import datetime
from src.core.memory import MemoryManager
from src.core.models import AgentContext

class AgentMemoryIntegration:
    """Integração de memória entre agentes."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
    
    async def store_agent_context(
        self,
        agent_id: str,
        context: AgentContext,
        ttl: Optional[int] = 3600  # 1 hora
    ):
        """Armazena contexto do agente na memória compartilhada."""
        key = f"agent:{agent_id}:context:{context.session_id}"
        await self.memory.store(key, context.dict(), ttl)
    
    async def get_agent_context(
        self,
        agent_id: str,
        session_id: str
    ) -> Optional[AgentContext]:
        """Recupera contexto do agente."""
        key = f"agent:{agent_id}:context:{session_id}"
        data = await self.memory.get(key)
        return AgentContext.parse_obj(data) if data else None
    
    async def share_context(
        self,
        from_agent: str,
        to_agent: str,
        session_id: str,
        context_type: str
    ):
        """Compartilha contexto entre agentes."""
        source = await self.get_agent_context(from_agent, session_id)
        if source:
            await self.store_agent_context(to_agent, source) 