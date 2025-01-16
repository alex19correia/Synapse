import pytest
from src.analytics.exporters import MetricsExporter
import pandas as pd
from pathlib import Path
from prometheus_client import Counter

@pytest.fixture
def exporter():
    return MetricsExporter()

@pytest.mark.asyncio
class TestMetricsExporter:
    async def test_prometheus_export(self, exporter):
        """Testa exportação no formato Prometheus"""
        # Criar algumas métricas de teste
        c = Counter('test_counter', 'A test counter', registry=exporter.registry)
        c.inc()
        
        metrics = await exporter.export_prometheus()
        assert isinstance(metrics, bytes)
        assert len(metrics) > 0
    
    async def test_csv_export(self, exporter, tmp_path):
        """Testa exportação para CSV"""
        test_metrics = {
            "metric1": [1, 2, 3],
            "metric2": [4, 5, 6]
        }
        
        exporter.export_path = tmp_path
        await exporter.export_csv(test_metrics, "test_export")
        
        files = list(tmp_path.glob("*.csv"))
        assert len(files) == 1
        
        df = pd.read_csv(files[0])
        assert list(df.columns) == ["metric1", "metric2"] 