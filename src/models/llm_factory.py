from typing import Union
from pydantic import BaseModel
from typing import Optional
from src.config import settings

class LLMConfig(BaseModel):
    provider: str
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    rate_limit: Optional[int] = None

    @classmethod
    def from_settings(cls):
        return cls(
            provider=settings.LLM_PROVIDER,
            api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            rate_limit=settings.LLM_RATE_LIMIT
        )

class LLMFactory:
    @staticmethod
    def get_llm(config: LLMConfig):
        if config.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=config.api_key)
        elif config.provider == "ollama":
            from ollama import Client
            return Client(base_url=config.base_url)
        else:
            raise ValueError(f"Provedor LLM não suportado: {config.provider}") 