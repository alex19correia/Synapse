import pytest
from src.core.workflow import WorkflowEngine
from src.core.agents import AgentRegistry
from src.core.memory import MemoryManager

@pytest.fixture
async def workflow_engine():
    memory = MemoryManager()
    registry = AgentRegistry()
    return WorkflowEngine(memory=memory, registry=registry)

@pytest.mark.integration
class TestWorkflowExecution:
    async def test_complete_workflow(self, workflow_engine):
        # Arrange
        workflow_config = {
            "steps": [
                {"agent": "web_researcher", "action": "search"},
                {"agent": "tech_stack_expert", "action": "analyze"},
                {"agent": "github_assistant", "action": "recommend"}
            ]
        }
        
        # Act
        result = await workflow_engine.execute(
            workflow_config,
            input_data={"query": "modern web app stack"}
        )
        
        # Assert
        assert "research" in result
        assert "analysis" in result
        assert "recommendations" in result 