from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Synapse API"
    API_DESCRIPTION: str = "AI Assistant API"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10  # Number of requests allowed
    RATE_LIMIT_TIME: int = 60      # Time window in seconds
    
    # Versão da API
    api_version: str = "v1"
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configurações do Supabase
    supabase_url: str
    supabase_key: str
    
    # Configurações de LLM
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Configurações de logging
    log_level: str = "INFO"
    
    # Configuração do Brave API
    brave_api_key: str | None = None
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância cacheada das configurações."""
    return Settings() 