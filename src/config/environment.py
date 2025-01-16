from typing import Optional
from pydantic import BaseSettings, Field, validator
from loguru import logger

class Environment(BaseSettings):
    """Configurações do ambiente da aplicação."""
    
    # Supabase
    SUPABASE_URL: str = Field(..., description="URL do projeto Supabase")
    SUPABASE_KEY: str = Field(..., description="Chave de API do Supabase")
    
    # LLMs
    OPENAI_API_KEY: Optional[str] = Field(None, description="Chave de API da OpenAI")
    COHERE_API_KEY: Optional[str] = Field(None, description="Chave de API da Cohere")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Chave de API do Google")
    
    # Servidor
    HOST: str = Field("0.0.0.0", description="Host do servidor")
    PORT: int = Field(8000, description="Porta do servidor")
    LOG_LEVEL: str = Field("INFO", description="Nível de logging")
    
    @validator("SUPABASE_URL")
    def validate_supabase_url(cls, v: str) -> str:
        """Valida o URL do Supabase."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("SUPABASE_URL deve começar com http:// ou https://")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Valida o nível de logging."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL deve ser um dos seguintes: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator("PORT")
    def validate_port(cls, v: int) -> int:
        """Valida a porta do servidor."""
        if not 1024 <= v <= 65535:
            raise ValueError("PORT deve estar entre 1024 e 65535")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def load_environment() -> Environment:
    """Carrega e valida as variáveis de ambiente."""
    try:
        env = Environment()
        logger.info("✅ Variáveis de ambiente carregadas com sucesso")
        return env
    except Exception as e:
        logger.error(f"❌ Erro ao carregar variáveis de ambiente: {str(e)}")
        raise 