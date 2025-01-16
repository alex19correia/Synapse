from pydantic import BaseModel, Field, validator

class LLMConfig(BaseModel):
    """Configuração do LLM."""
    
    provider: str = "mock"
    model_name: str = "mock-model"
    api_key: str = "test-key"
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = 1000
    cache_ttl: int = 3600  # 1 hora 