from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Base settings for the application."""
    app_name: str = "Synapse API"
    debug: bool = True
    environment: str = "development"
    
    # API Settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379"
    
    # LLM Settings
    model_name: str = "deepseek"
    
    class Config:
        env_prefix = "SYNAPSE_"

def get_settings() -> Settings:
    """Get application settings."""
    return Settings() 