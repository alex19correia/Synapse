from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from rich.console import Console
from pathlib import Path

console = Console()

class MetricsVisualizer:
    """Gerador de visualizações personalizadas"""
    
    def __init__(self):
        self.output_dir = Path("visualizations")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurações de tema
        self.theme = {
            "background": "#1a1a1a",
            "text": "#ffffff",
            "primary": "#00ff00",
            "secondary": "#ff00ff"
        }
    
    async def create_retention_heatmap(self, data: pd.DataFrame):
        """Cria heatmap de retenção"""
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title="User Retention Heatmap",
            xaxis_title="Days",
            yaxis_title="Cohort",
            template="plotly_dark"
        )
        
        return fig
    
    async def create_feature_usage_sunburst(self, data: Dict[str, Any]):
        """Cria sunburst de uso de features"""
        fig = px.sunburst(
            data,
            path=['category', 'feature'],
            values='usage_count',
            color='usage_count'
        )
        
        fig.update_layout(
            title="Feature Usage Distribution",
            template="plotly_dark"
        )
        
        return fig
    
    async def create_satisfaction_gauge(self, score: float):
        """Cria gauge de satisfação"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 5]},
                'bar': {'color': self.theme['primary']},
                'steps': [
                    {'range': [0, 2], 'color': "red"},
                    {'range': [2, 3.5], 'color': "yellow"},
                    {'range': [3.5, 5], 'color': "green"}
                ]
            }
        ))
        
        fig.update_layout(
            title="User Satisfaction Score",
            template="plotly_dark"
        )
        
        return fig
    
    async def save_visualization(self, fig: go.Figure, name: str):
        """Salva visualização em HTML e PNG"""
        try:
            html_path = self.output_dir / f"{name}_{datetime.now():%Y%m%d}.html"
            png_path = self.output_dir / f"{name}_{datetime.now():%Y%m%d}.png"
            
            fig.write_html(str(html_path))
            fig.write_image(str(png_path))
            
            console.print(f"[green]Visualização salva em {html_path} e {png_path}[/green]")
        except Exception as e:
            console.print(f"[error]Erro ao salvar visualização: {e}[/error]") 