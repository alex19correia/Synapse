from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class BrowserSettings(BaseModel):
    """Configurações do navegador"""
    headless: bool = True
    timeout: int = 30000  # em milissegundos
    user_data_dir: Optional[str] = None
    use_persistent_context: bool = True
    verbose: bool = False

class ExtractionSettings(BaseModel):
    """Configurações de extração de conteúdo"""
    use_llm: bool = False
    max_retries: int = 3
    retry_delay: int = 1000  # em milissegundos
    extract_metadata: bool = True

class CrawlerConfig(BaseModel):
    """Configuração completa do crawler"""
    max_concurrent: int = Field(default=5, ge=1, le=10)
    batch_size: int = Field(default=10, ge=1, le=50)
    browser_settings: BrowserSettings = Field(default_factory=BrowserSettings)
    extraction_settings: ExtractionSettings = Field(default_factory=ExtractionSettings)
    
    class Config:
        arbitrary_types_allowed = True

# Configuração padrão
default_config = CrawlerConfig() 