from typing import Any, Dict, Optional
import structlog
from datetime import datetime

class AgentLogger:
    """Logger estruturado para agentes."""
    
    def __init__(self, service_name: str):
        self.logger = structlog.get_logger(service_name)
        self.context = {}
    
    def add_context(self, **kwargs):
        """Adiciona contexto ao logger."""
        self.context.update(kwargs)
    
    async def info(self, event: str, **kwargs):
        """Log de informação."""
        self._log("info", event, **kwargs)
    
    async def error(self, event: str, error: Optional[Exception] = None, **kwargs):
        """Log de erro."""
        extra = {"error": str(error)} if error else {}
        self._log("error", event, **{**kwargs, **extra})
    
    async def debug(self, event: str, **kwargs):
        """Log de debug."""
        self._log("debug", event, **kwargs)
    
    def _log(self, level: str, event: str, **kwargs):
        """Método interno de logging."""
        self.logger.bind(**self.context).log(
            level,
            event=event,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        ) 