from typing import Dict, Any
from enum import Enum
import asyncio

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertService:
    def __init__(self, config: Dict[str, Any]):
        self.slack_webhook = config["SLACK_WEBHOOK"]
        self.alert_thresholds = {
            "failed_login_attempts": 5,
            "api_error_rate": 0.05,  # 5%
            "response_time_ms": 2000  # 2 segundos
        }
    
    async def trigger_alert(self, level: AlertLevel, message: str, metadata: Dict[str, Any]):
        """Dispara alertas para diferentes canais"""
        if level == AlertLevel.CRITICAL:
            # Notificar Slack e email
            await asyncio.gather(
                self._notify_slack(message, metadata),
                self._send_email_alert(message, metadata)
            )
        else:
            # Apenas Slack para não-críticos
            await self._notify_slack(message, metadata) 