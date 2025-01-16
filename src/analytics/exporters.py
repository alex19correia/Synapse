from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
from prometheus_client import CollectorRegistry, generate_latest
import json
from rich.console import Console
from pathlib import Path
import asyncio

console = Console()

class MetricsExporter:
    """Exportador de métricas para diferentes formatos"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.export_path = Path("exports")
        self.export_path.mkdir(exist_ok=True)
    
    async def export_prometheus(self) -> bytes:
        """Exporta métricas no formato Prometheus"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            console.print(f"[error]Erro ao exportar métricas Prometheus: {e}[/error]")
            return b""
    
    async def export_csv(self, metrics: Dict[str, Any], filename: str):
        """Exporta métricas para CSV"""
        try:
            df = pd.DataFrame(metrics)
            export_file = self.export_path / f"{filename}_{datetime.now():%Y%m%d}.csv"
            df.to_csv(export_file, index=False)
            console.print(f"[green]Métricas exportadas para {export_file}[/green]")
        except Exception as e:
            console.print(f"[error]Erro ao exportar CSV: {e}[/error]")
    
    async def export_json(self, metrics: Dict[str, Any], filename: str):
        """Exporta métricas para JSON"""
        try:
            export_file = self.export_path / f"{filename}_{datetime.now():%Y%m%d}.json"
            with open(export_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            console.print(f"[green]Métricas exportadas para {export_file}[/green]")
        except Exception as e:
            console.print(f"[error]Erro ao exportar JSON: {e}[/error]") 