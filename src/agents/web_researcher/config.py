from pydantic import BaseSettings

class WebResearcherConfig(BaseSettings):
    brave_api_key: str | None = None
    max_results: int = 3
    search_lang: str = "en"
    
    class Config:
        env_prefix = "SYNAPSE_WEB_" 