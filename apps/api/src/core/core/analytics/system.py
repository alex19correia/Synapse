from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd
from src.core.monitoring import MonitoringIntegration

class AgentAnalytics(BaseModel):
    """Analytics por agente."""
    success_rate: float
    avg_response_time: float
    usage_count: int
    feedback_score: float
    common_issues: List[str]

class AnalyticsSystem:
    """Sistema central de analytics."""
    
    def __init__(self, monitoring: MonitoringIntegration):
        self.monitoring = monitoring
        self.db = self._init_database()
    
    async def collect_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, AgentAnalytics]:
        """Coleta métricas de todos os agentes."""
        metrics = {}
        
        for agent_id in await self._get_active_agents():
            metrics[agent_id] = await self._analyze_agent(
                agent_id,
                start_time,
                end_time
            )
        
        return metrics
    
    async def generate_report(
        self,
        timeframe: str = "daily"
    ) -> Dict:
        """Gera relatório de performance."""
        end_time = datetime.utcnow()
        start_time = self._get_start_time(timeframe, end_time)
        
        metrics = await self.collect_metrics(start_time, end_time)
        return {
            "timeframe": timeframe,
            "generated_at": end_time,
            "metrics": metrics,
            "recommendations": await self._generate_recommendations(metrics)
        }
    
    async def _analyze_agent(
        self,
        agent_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> AgentAnalytics:
        """Analisa performance de um agente específico."""
        data = await self._fetch_agent_data(agent_id, start_time, end_time)
        
        return AgentAnalytics(
            success_rate=self._calculate_success_rate(data),
            avg_response_time=self._calculate_avg_response_time(data),
            usage_count=len(data),
            feedback_score=self._calculate_feedback_score(data),
            common_issues=self._identify_common_issues(data)
        ) 