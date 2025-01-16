from typing import Dict
from pydantic import BaseModel, ConfigDict

class BaseAgent(BaseModel):
    name: str = "Base Agent"
    description: str = "Agente base para outros agentes"
    version: str = "1.0.0"
    confidence_threshold: float = 0.7
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Verifica se o agente pode lidar com a query"""
        return 0.0
    
    async def process_query(self, query: str, context: Dict) -> Dict:
        """Processa a query e retorna resposta"""
        raise NotImplementedError("Método process_query deve ser implementado") 