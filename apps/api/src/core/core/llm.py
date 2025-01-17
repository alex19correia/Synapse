from typing import Optional
from src.core.memory import MemorySystem
from src.core.retrieval import RetrievalSystem
from src.core.tools import ToolManager

class LLMSystem:
    def __init__(
        self,
        memory_system: Optional[MemorySystem] = None,
        retrieval_system: Optional[RetrievalSystem] = None,
        tool_manager: Optional[ToolManager] = None
    ):
        self.memory_system = memory_system or MemorySystem()
        self.retrieval_system = retrieval_system or RetrievalSystem()
        self.tool_manager = tool_manager or ToolManager() 