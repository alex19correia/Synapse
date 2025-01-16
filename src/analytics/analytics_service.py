from typing import Dict, Any, Optional
from posthog import Posthog
import os
from rich.console import Console
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()

class AnalyticsService:
    """Serviço de analytics usando PostHog"""
    
    def __init__(self):
        api_key = os.getenv("POSTHOG_API_KEY", "test_api_key")
        self.posthog = Posthog(
            project_api_key=api_key,
            host=os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        )
        
        # Métricas core definidas em analytics-system.md
        self.core_metrics = {
            "user_engagement": ["session_duration", "messages_sent", "features_used"],
            "llm_performance": ["response_time", "token_usage", "cache_hits"],
            "system_health": ["error_rate", "latency", "memory_usage"]
        }
        
        # Thresholds para alertas
        self.thresholds = {
            "error_rate": 0.05,  # 5%
            "latency": 2000,     # 2 segundos
            "memory_usage": 0.85  # 85%
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def track_event(
        self,
        event_name: str,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Registra um evento no PostHog"""
        try:
            self.posthog.capture(
                distinct_id=user_id,
                event=event_name,
                properties=properties or {}
            )
        except Exception as e:
            console.print(f"[error]Erro ao registrar evento: {e}[/error]")
            raise
    
    async def track_conversation(
        self,
        user_id: str,
        message_count: int,
        duration: float,
        success: bool
    ):
        """Registra métricas de conversação"""
        await self.track_event(
            "conversation_completed",
            user_id,
            {
                "message_count": message_count,
                "duration_seconds": duration,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def track_llm_usage(
        self,
        user_id: str,
        model: str,
        tokens_used: int,
        response_time: float,
        cache_hit: bool
    ):
        """Registra métricas de uso do LLM"""
        await self.track_event(
            "llm_request",
            user_id,
            {
                "model": model,
                "tokens": tokens_used,
                "response_time": response_time,
                "cache_hit": cache_hit,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def check_thresholds(self, metrics: Dict[str, float]):
        """Verifica se métricas ultrapassaram thresholds"""
        for metric, value in metrics.items():
            if metric in self.thresholds and value > self.thresholds[metric]:
                await self.track_event(
                    "threshold_exceeded",
                    "system",
                    {
                        "metric": metric,
                        "value": value,
                        "threshold": self.thresholds[metric],
                        "timestamp": datetime.now().isoformat()
                    }
                )
    
    async def track_cache_operation(
        self,
        operation: str,
        hit: bool
    ):
        """Registra operações de cache"""
        await self.track_event(
            "cache_operation",
            "system",
            {
                "operation": operation,
                "hit": hit,
                "timestamp": datetime.now().isoformat()
            }
        ) 