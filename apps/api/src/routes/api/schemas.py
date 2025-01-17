"""
API schemas.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[Message]
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False
    use_rag: bool = False

class ChatChoice(BaseModel):
    """Chat completion choice."""
    message: Dict[str, str]
    finish_reason: str

class ChatUsage(BaseModel):
    """Chat completion usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    """Chat completion response."""
    id: str
    choices: List[ChatChoice]
    usage: ChatUsage 