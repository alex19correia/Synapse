"""API schemas."""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal

class Message(BaseModel):
    """Chat message."""
    role: Literal["user", "assistant", "system"] = Field(
        ..., 
        description="The role of the message sender"
    )
    content: str = Field(
        ...,
        description="The content of the message"
    )

class ChatCompletionRequest(BaseModel):
    """Chat completion request."""
    messages: List[Message] = Field(
        ...,
        description="The messages to generate a completion for"
    )
    model: str = Field(
        ...,
        description="The model to use for completion"
    )
    use_rag: bool = Field(
        False,
        description="Whether to use RAG for completion"
    )
    
    @validator("messages")
    def validate_messages(cls, v):
        """Validate messages."""
        if not v:
            raise ValueError("At least one message is required")
        return v

class ChatCompletionResponse(BaseModel):
    """Chat completion response."""
    response: str = Field(
        ...,
        description="The generated completion"
    )
    usage: Dict[str, int] = Field(
        ...,
        description="Token usage statistics"
    )

class Document(BaseModel):
    """Document for indexing."""
    content: str = Field(
        ...,
        description="The content of the document"
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description="Optional metadata about the document"
    ) 