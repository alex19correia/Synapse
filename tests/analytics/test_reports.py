import pytest
from src.analytics.reports import ReportGenerator
from unittest.mock import Mock, patch

@pytest.fixture
def report_generator():
    return ReportGenerator()

@pytest.mark.asyncio
class TestReportGenerator:
    async def test_daily_report_generation(self, report_generator):
        """Testa geração de relatório diário"""
        test_metrics = {
            "users": 100,
            "interactions": 500,
            "satisfaction": 4.5
        }
        
        report = await report_generator.generate_daily_report(test_metrics)
        assert isinstance(report, str)
        assert "users" in report
        assert "interactions" in report
    
    @patch('aiosmtplib.send')
    async def test_email_sending(self, mock_send, report_generator):
        """Testa envio de email"""
        test_report = "<h1>Test Report</h1>"
        test_recipients = ["test@example.com"]
        
        await report_generator.send_report_email(test_report, test_recipients)
        mock_send.assert_called_once() 