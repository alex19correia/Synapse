"""Configurações para testes."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class TestSettings(BaseSettings):
    """Configurações de teste"""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supabase
    SUPABASE_URL: str = "https://test.supabase.co"
    SUPABASE_KEY: str = "test-key"
    
    # Clerk
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str = "pk_test"
    CLERK_SECRET_KEY: str = "sk_test"
    CLERK_TEST_TOKEN: str = "test_token"
    CLERK_PUBLISHABLE_KEY: str = "pk_test"
    
    # LLM
    DEEPSEEK_API_KEY: str = "test-key"
    OPENAI_API_KEY: str = "test-key"
    COHERE_API_KEY: str = "test-key"
    GOOGLE_API_KEY: str = "test-key"
    MODEL_NAME: str = "deepseek-chat"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # Rate Limiting
    REQUESTS_PER_SECOND: int = 2
    MAX_REQUESTS_PER_DOMAIN: int = 100
    COOLDOWN_PERIOD: int = 60
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_TIME: int = 60
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "DEBUG"
    
    # JWT
    JWT_SECRET_KEY: str = "test-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # Email
    SMTP_HOST: str = "smtp.test.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "test@test.com"
    SMTP_PASSWORD: str = "test-pass"
    EMAIL_FROM: str = "test@test.com"
    
    # Analytics
    POSTHOG_API_KEY: str = "test-key"
    POSTHOG_HOST: str = "https://test.posthog.com"
    
    # Vector DB
    QDRANT_URL: str = "http://localhost:6335"
    QDRANT_API_KEY: str = "test-key"
    QDRANT_TIMEOUT: float = 10.0
    QDRANT_COLLECTION: str = "test_collection"
    
    # GitHub
    GITHUB_TOKEN: str = "test-token"
    
    # Brave
    BRAVE_API_KEY: str = "test-key"
    
    # Environment
    ENV: str = "test"
    
    model_config = ConfigDict(
        env_file=None,
        env_file_encoding="utf-8"
    )

# Instância global para testes
test_settings = TestSettings() 