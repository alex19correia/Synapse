from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from pathlib import Path
import jinja2
import aiofiles
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import os

console = Console()

class ReportGenerator:
    """Gerador de relatórios automáticos"""
    
    def __init__(self):
        self.template_dir = Path("templates/reports")
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir))
        )
        
        # Configurações de email
        self.smtp_config = {
            "hostname": "smtp.gmail.com",
            "port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password"
        }
    
    async def generate_daily_report(self, metrics: Dict[str, Any]) -> str:
        """Gera relatório diário"""
        try:
            template = self.env.get_template("daily_report.html")
            return template.render(
                metrics=metrics,
                date=datetime.now().strftime("%Y-%m-%d")
            )
        except Exception as e:
            console.print(f"[error]Erro ao gerar relatório: {e}[/error]")
            return ""
    
    async def send_report_email(self, report: str, recipients: List[str]):
        """Envia relatório por email"""
        try:
            message = MIMEMultipart()
            message["Subject"] = f"Synapse Daily Report - {datetime.now():%Y-%m-%d}"
            message["From"] = self.smtp_config["username"]
            message["To"] = ", ".join(recipients)
            
            message.attach(MIMEText(report, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_config["hostname"],
                port=self.smtp_config["port"],
                username=self.smtp_config["username"],
                password=self.smtp_config["password"],
                use_tls=True
            )
            
            console.print("[green]Relatório enviado com sucesso![/green]")
        except Exception as e:
            console.print(f"[error]Erro ao enviar relatório: {e}[/error]")
    
    async def schedule_reports(self):
        """Agenda geração e envio de relatórios"""
        while True:
            now = datetime.now()
            # Aguarda até próximo relatório (00:00)
            next_report = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            await asyncio.sleep((next_report - now).total_seconds())
            
            # Gera e envia relatório
            metrics = await self.collect_daily_metrics()
            report = await self.generate_daily_report(metrics)
            await self.send_report_email(report, ["team@synapse.ai"])
    
    async def collect_daily_metrics(self) -> Dict[str, Any]:
        """Coleta métricas diárias"""
        # Implementação real buscaria métricas do Prometheus/PostHog
        return {} 

# Verificar se o template existe
template_path = Path("templates/reports/daily_report.html")
if not template_path.exists():
    print(f"Template não encontrado em: {template_path.absolute()}")
    # Criar o template se não existir
    template_path.parent.mkdir(parents=True, exist_ok=True)
    with open(template_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Daily Report</title>
</head>
<body>
    <h1>Daily Report - {{ date }}</h1>
    
    <h2>Metrics Summary</h2>
    <ul>
        {% for key, value in metrics.items() %}
        <li><strong>{{ key }}:</strong> {{ value }}</li>
        {% endfor %}
    </ul>
</body>
</html>""") 