from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class LLMProvider(str, Enum):
    """Enum para provedores de LLM."""
    OPENAI = "openai"
    COHERE = "cohere"
    GOOGLE = "google"
    OLLAMA = "ollama"

class LLMRole(str, Enum):
    """Enum para papéis em uma conversa com LLM."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class LLMMessage(BaseModel):
    """Modelo para mensagens trocadas com LLM."""
    role: LLMRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LLMContext(BaseModel):
    """Modelo para contexto da conversa com LLM."""
    messages: List[LLMMessage] = Field(default_factory=list)
    user_id: str
    session_id: str
    provider: LLMProvider
    model: str
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LLMResponse(BaseModel):
    """Modelo para respostas do LLM."""
    content: str
    role: LLMRole = Field(default=LLMRole.ASSISTANT)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: LLMProvider
    model: str
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LLMPrompt(BaseModel):
    """Modelo para prompts enviados ao LLM."""
    content: str
    context: Optional[LLMContext] = None
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LLMConfig(BaseModel):
    """Modelo para configuração de LLM."""
    provider: LLMProvider
    model: str
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict) 