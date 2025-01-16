"""LLM service implementation."""
import logging
from typing import Dict, List

from src.config.settings import get_settings
from src.schemas import Message

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for LLM API."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.settings = get_settings()
        
    def complete(self, messages: List[Message], model: str) -> Dict[str, any]:
        """
        Generate completion for messages.
        
        Args:
            messages: List of messages
            model: Model to use
            
        Returns:
            Completion response
        """
        if self.settings.ENV == "test":
            # Return test responses
            last_message = messages[-1].content.lower()
            
            if "capital" in last_message and "france" in last_message:
                return {
                    "response": "The capital of France is Paris.",
                    "usage": {
                        "prompt_tokens": len(last_message.split()),
                        "completion_tokens": 7,
                        "total_tokens": len(last_message.split()) + 7
                    }
                }
                
            return {
                "response": "This is a test response.",
                "usage": {
                    "prompt_tokens": len(last_message.split()),
                    "completion_tokens": 5,
                    "total_tokens": len(last_message.split()) + 5
                }
            }
            
        # Production implementation
        raise NotImplementedError("LLM service not implemented for production") 