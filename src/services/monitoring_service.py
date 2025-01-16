from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class LLMMetrics:
    tokens_used: int
    response_time_ms: int
    cache_hit: bool
    model_name: str
    timestamp: datetime = datetime.now()

class MonitoringService:
    def __init__(self):
        self.metrics: Dict[str, list] = {
            "daily_tokens": [],
            "response_times": [],
            "cache_hits": []
        }
        
    async def track_llm_usage(self, metrics: LLMMetrics) -> None:
        """
        Regista métricas de uso do LLM
        """
        self.metrics["daily_tokens"].append(metrics.tokens_used)
        self.metrics["response_times"].append(metrics.response_time_ms)
        self.metrics["cache_hits"].append(metrics.cache_hit)
        
        # Verifica limites e dispara alertas se necessário
        await self._check_usage_limits(metrics)
        
    async def _check_usage_limits(self, metrics: LLMMetrics) -> None:
        """
        Verifica se os limites de uso foram excedidos
        """
        daily_tokens = sum(self.metrics["daily_tokens"])
        if daily_tokens > self.config.daily_token_limit:
            await self._send_alert(f"Token limit exceeded: {daily_tokens}") 