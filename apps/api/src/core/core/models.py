from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class AgentContext(BaseModel):
    """Modelo para contexto de agentes."""
    session_id: str
    agent_id: str
    timestamp: datetime = datetime.utcnow()
    metadata: Dict[str, Any] = {}
    state: Dict[str, Any] = {}
    memory_refs: Optional[Dict[str, str]] = None 