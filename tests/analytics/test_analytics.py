import pytest
from unittest.mock import Mock, patch
from src.analytics.analytics_service import AnalyticsService

@pytest.fixture
def mock_posthog():
    with patch('posthog.Posthog', autospec=True) as mock:
        # Configurar o mock para retornar uma API key válida
        mock.return_value.api_key = "test_api_key"
        yield mock

@pytest.fixture
def analytics_service():
    # Criar uma instância do AnalyticsService com uma API key de teste
    with patch.dict('os.environ', {'POSTHOG_API_KEY': 'test_api_key'}):
        service = AnalyticsService()
        return service

@pytest.mark.asyncio
class TestAnalytics:
    async def test_track_event(self, analytics_service):
        """Testa tracking básico de eventos"""
        with patch.object(analytics_service.posthog, 'capture') as mock_capture:
            await analytics_service.track_event(
                "test_event",
                "user_123",
                {"test": "data"}
            )
            mock_capture.assert_called_once()
    
    async def test_llm_metrics(self, analytics_service):
        """Testa métricas de LLM"""
        with patch.object(analytics_service.posthog, 'capture') as mock_capture:
            await analytics_service.track_llm_usage(
                "user_123",
                "gpt-4",
                100,
                0.5,
                False
            )
            mock_capture.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_alert_thresholds(self, analytics_service):
        """Testa thresholds de alerta"""
        with patch.object(analytics_service.posthog, 'capture') as mock_capture:
            await analytics_service.check_thresholds({
                "error_rate": 0.06  # Acima do threshold
            })
            mock_capture.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_metrics(self, analytics_service):
        """Testa métricas de cache"""
        with patch.object(analytics_service.posthog, 'capture') as mock_capture:
            await analytics_service.track_cache_operation("get", True)
            mock_capture.assert_called_once() 