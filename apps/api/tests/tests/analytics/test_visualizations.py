import pytest
import pandas as pd
import plotly.graph_objects as go
from src.analytics.visualizations import MetricsVisualizer

@pytest.fixture
def visualizer():
    return MetricsVisualizer()

@pytest.mark.asyncio
class TestMetricsVisualizer:
    async def test_retention_heatmap(self, visualizer):
        """Testa criação de heatmap"""
        test_data = pd.DataFrame({
            'Week 1': [100, 90, 80],
            'Week 2': [90, 85, 75],
            'Week 3': [80, 75, 70]
        })
        
        fig = await visualizer.create_retention_heatmap(test_data)
        assert isinstance(fig, go.Figure)
    
    async def test_feature_usage_sunburst(self, visualizer):
        """Testa criação de sunburst"""
        test_data = {
            'category': ['A', 'A', 'B'],
            'feature': ['X', 'Y', 'Z'],
            'usage_count': [10, 20, 30]
        }
        
        fig = await visualizer.create_feature_usage_sunburst(test_data)
        assert isinstance(fig, go.Figure)
    
    async def test_satisfaction_gauge(self, visualizer):
        """Testa criação de gauge"""
        fig = await visualizer.create_satisfaction_gauge(4.5)
        assert isinstance(fig, go.Figure) 