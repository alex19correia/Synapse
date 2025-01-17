from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Enum para os diferentes papéis em uma mensagem."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    """Modelo para mensagens individuais."""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default_factory=dict)

class ChatSession(BaseModel):
    """Modelo para sessões de chat."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    title: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    """Modelo para requisições de chat."""
    message: str
    session_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None

class ChatResponse(BaseModel):
    """Modelo para respostas de chat."""
    response: str
    session_id: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    metadata: Optional[dict] = None 