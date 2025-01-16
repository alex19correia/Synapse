from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel

class QualityMetrics(BaseModel):
    """Métricas de qualidade do código."""
    test_coverage: float
    code_smells: int
    maintainability_index: float
    cyclomatic_complexity: float

class QualityMonitor:
    """Monitor de qualidade de código."""
    
    def __init__(self):
        self.metrics_history: List[Dict] = []
    
    async def collect_metrics(self) -> QualityMetrics:
        """Coleta métricas de qualidade."""
        coverage = await self._get_test_coverage()
        smells = await self._analyze_code_smells()
        maintainability = await self._calculate_maintainability()
        complexity = await self._calculate_complexity()
        
        metrics = QualityMetrics(
            test_coverage=coverage,
            code_smells=smells,
            maintainability_index=maintainability,
            cyclomatic_complexity=complexity
        )
        
        self.metrics_history.append({
            "timestamp": datetime.utcnow(),
            "metrics": metrics.dict()
        })
        
        return metrics
    
    async def generate_report(self) -> Dict:
        """Gera relatório de qualidade."""
        current_metrics = await self.collect_metrics()
        historical_data = self.metrics_history[-10:]  # Últimas 10 medições
        
        return {
            "current": current_metrics.dict(),
            "historical": historical_data,
            "trends": await self._analyze_trends(historical_data),
            "recommendations": await self._generate_recommendations(current_metrics)
        } 