from typing import Optional
from datetime import datetime
from .agent_metrics import AgentMetrics
from .logger import AgentLogger
from .health import HealthCheck

class MonitoringIntegration:
    """Integração central de monitoramento."""
    
    def __init__(self, service_name: str):
        self.metrics = AgentMetrics()
        self.logger = AgentLogger(service_name)
        self.health = HealthCheck()
        
        # Registra health checks padrão
        self._register_default_health_checks()
    
    async def track_agent_operation(
        self,
        agent_id: str,
        operation: str,
        context: Optional[dict] = None
    ):
        """Tracks uma operação completa do agente."""
        async with self.metrics.track_latency(agent_id, operation):
            # Adiciona contexto ao logger
            self.logger.add_context(
                agent_id=agent_id,
                operation=operation,
                **context or {}
            )
            
            await self.logger.info(
                f"Starting {operation}",
                start_time=datetime.utcnow().isoformat()
            )
            
            try:
                # Aqui o agente executa sua operação
                yield
                
                await self.metrics.record_query(agent_id, "success")
                await self.logger.info(f"Completed {operation}")
                
            except Exception as e:
                await self.metrics.record_query(agent_id, "error")
                await self.logger.error(
                    f"Failed {operation}",
                    error=e
                )
                raise 