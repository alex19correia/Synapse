from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str
    LLM_MODEL_NAME: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    LLM_RATE_LIMIT: int = 30
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()

# Exporta a classe Settings
__all__ = ["Settings", "get_settings"]


