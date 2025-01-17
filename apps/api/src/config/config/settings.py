"""
Application settings for Synapse.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("ENV") == "test" else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from env
    )
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Redis settings
    REDIS_URL: Optional[str] = None
    
    # LLM settings
    DEEPSEEK_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "deepseek-chat"  # Default to DeepSeek
    MODEL_NAME: str = "deepseek-chat"  # Default model
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_TIME: int = 60
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    # JWT settings
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # SMTP settings
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    # PostHog settings
    POSTHOG_API_KEY: Optional[str] = None
    POSTHOG_HOST: str = "https://app.posthog.com"
    
    # Qdrant settings
    QDRANT_URL: str = "http://localhost:6335"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_TIMEOUT: float = 10.0
    QDRANT_COLLECTION: str = "synapse_collection"
    
    # GitHub settings
    GITHUB_TOKEN: Optional[str] = None
    
    # Brave settings
    BRAVE_API_KEY: Optional[str] = None
    
    # Monitoring
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()