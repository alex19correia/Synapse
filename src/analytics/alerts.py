from typing import Dict, Any
import os
from rich.console import Console
from datetime import datetime
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()

class AlertSystem:
    """Sistema de alertas para métricas críticas"""
    
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "p95_latency": 2000,  # 2 seconds
            "memory_usage": 0.85  # 85% usage
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_alert(self, alert_type: str, details: Dict[str, Any]):
        """Envia alerta via Slack"""
        try:
            if self.slack_webhook:
                message = self._format_alert(alert_type, details)
                requests.post(self.slack_webhook, json={"text": message})
        except Exception as e:
            console.print(f"[error]Erro ao enviar alerta: {e}[/error]")
            raise
    
    def _format_alert(self, alert_type: str, details: Dict[str, Any]) -> str:
        """Formata mensagem de alerta"""
        return f"""
🚨 *ALERTA: {alert_type}*
Detalhes: {details}
Timestamp: {datetime.now().isoformat()}
        """.strip()
    
    async def check_thresholds(self, metrics: Dict[str, float]):
        """Verifica se métricas ultrapassaram thresholds"""
        for metric, value in metrics.items():
            if metric in self.thresholds and value > self.thresholds[metric]:
                await self.send_alert(
                    f"Threshold Exceeded: {metric}",
                    {
                        "metric": metric,
                        "value": value,
                        "threshold": self.thresholds[metric]
                    }
                ) 