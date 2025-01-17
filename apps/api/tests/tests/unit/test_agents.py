import pytest
from unittest.mock import AsyncMock, patch
from src.core.agents import BaseSpecializedAgent
from src.core.memory import MemoryManager
from src.core.monitoring import MonitoringIntegration

@pytest.fixture
def mock_memory():
    return AsyncMock(spec=MemoryManager)

@pytest.fixture
def mock_monitoring():
    return AsyncMock(spec=MonitoringIntegration)

@pytest.fixture
def base_agent(mock_memory, mock_monitoring):
    agent_config = {
        "agent_id": "test-agent",
        "version": "1.0.0",
        "capabilities": ["test"]
    }
    return BaseSpecializedAgent(
        config=agent_config,
        memory=mock_memory,
        monitoring=mock_monitoring
    )

class TestBaseAgent:
    async def test_process_query(self, base_agent):
        # Arrange
        query = "test query"
        context = {"user_id": "123"}
        
        # Act
        result = await base_agent.process(query, context)
        
        # Assert
        assert result is not None
        base_agent.memory.store.assert_called_once()
        base_agent.monitoring.track_agent_operation.assert_called_once() 