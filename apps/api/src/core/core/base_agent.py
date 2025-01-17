from typing import Optional, Dict, Any

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self):
        self.memory = None
        self.cache = None
        
    async def process_message(self, message: str, user_id: Optional[str] = None) -> str:
        """Process a message and return a response."""
        raise NotImplementedError
        
    async def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return {
            "memory": self.memory,
            "cache": self.cache
        } 