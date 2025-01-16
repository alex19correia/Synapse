from typing import Dict, List, Any
from datetime import datetime
from pydantic import BaseModel

class HealthStatus(BaseModel):
    """Status de saúde do componente."""
    status: str  # "healthy", "degraded", "unhealthy"
    last_check: datetime
    details: Dict[str, Any]

class HealthCheck:
    """Sistema de health check."""
    
    def __init__(self):
        self.checks = {}
        self.last_status = {}
    
    async def register_check(self, component: str, check_fn):
        """Registra uma nova verificação de saúde."""
        self.checks[component] = check_fn
    
    async def run_checks(self) -> Dict[str, HealthStatus]:
        """Executa todas as verificações registradas."""
        results = {}
        
        for component, check_fn in self.checks.items():
            try:
                status = await check_fn()
                results[component] = HealthStatus(
                    status="healthy" if status else "unhealthy",
                    last_check=datetime.utcnow(),
                    details={"check_result": status}
                )
            except Exception as e:
                results[component] = HealthStatus(
                    status="unhealthy",
                    last_check=datetime.utcnow(),
                    details={"error": str(e)}
                )
        
        self.last_status = results
        return results 