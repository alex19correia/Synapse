from typing import Dict, Any, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Gauge, Histogram
from rich.console import Console

console = Console()

# Métricas de Retenção
user_retention = Gauge(
    'user_retention_days',
    'Days since last user interaction',
    ['user_id']
)

feature_usage = Counter(
    'feature_usage_count',
    'Usage count per feature',
    ['feature', 'user_id']
)

user_satisfaction = Histogram(
    'user_satisfaction_score',
    'User satisfaction scores',
    ['interaction_type'],
    buckets=[1, 2, 3, 4, 5]
)

class BusinessMetrics:
    """Gerenciador de métricas de negócio"""
    
    def __init__(self):
        self.console = Console()
        
    async def track_user_retention(self, user_id: str, last_active: datetime):
        """Atualiza métricas de retenção de usuário"""
        days_active = (datetime.now() - last_active).days
        user_retention.labels(user_id=user_id).set(days_active)
    
    async def track_feature_usage(self, user_id: str, feature: str):
        """Registra uso de features"""
        feature_usage.labels(
            feature=feature,
            user_id=user_id
        ).inc()
    
    async def track_satisfaction(
        self,
        score: int,
        interaction_type: str
    ):
        """Registra score de satisfação"""
        user_satisfaction.labels(
            interaction_type=interaction_type
        ).observe(score)
    
    async def calculate_metrics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas de negócio"""
        try:
            return {
                "daily_active_users": self._calculate_dau(),
                "feature_adoption_rate": self._calculate_feature_adoption(),
                "average_satisfaction": self._calculate_avg_satisfaction()
            }
        except Exception as e:
            console.print(f"[error]Erro ao calcular métricas: {e}[/error]")
            return {}
    
    def _calculate_dau(self) -> float:
        """Calcula usuários ativos diários"""
        # Implementação real usaria queries no banco de dados
        return 0.0
    
    def _calculate_feature_adoption(self) -> Dict[str, float]:
        """Calcula taxa de adoção por feature"""
        # Implementação real usaria queries no banco de dados
        return {}
    
    def _calculate_avg_satisfaction(self) -> float:
        """Calcula média de satisfação"""
        # Implementação real usaria queries no banco de dados
        return 0.0 