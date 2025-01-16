from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from src.core.monitoring import MonitoringIntegration

class AuditEvent(BaseModel):
    """Evento de auditoria."""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    status: str
    details: Optional[Dict[str, Any]] = None

class AuditSystem:
    """Sistema de auditoria de segurança."""
    
    def __init__(self, monitoring: MonitoringIntegration):
        self.monitoring = monitoring
        self._setup_audit_storage()
    
    async def log_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        status: str = "success",
        details: Optional[Dict] = None
    ):
        """Registra evento de auditoria."""
        event = AuditEvent(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            details=details
        )
        
        await self._store_event(event)
        await self._check_security_alerts(event)
    
    async def get_user_activity(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditEvent]:
        """Recupera atividade do usuário."""
        query = {"user_id": user_id}
        
        if start_time:
            query["timestamp"] = {"$gte": start_time}
        if end_time:
            query["timestamp"] = {"$lte": end_time}
            
        return await self._query_events(query)
    
    async def _check_security_alerts(self, event: AuditEvent):
        """Verifica por alertas de segurança."""
        if event.status == "failed":
            await self.monitoring.logger.warning(
                "Security alert",
                event=event.dict()
            ) 