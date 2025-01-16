from typing import Optional, List
from pydantic import BaseModel, Field

class TechStackRequirements(BaseModel):
    """Requisitos para análise de stack tecnológica."""
    app_description: str
    ai_coding_assistant: Optional[str] = None
    frontend_experience: List[str] = Field(default_factory=list)
    backend_experience: List[str] = Field(default_factory=list)
    user_scale: str
    specific_requirements: Optional[dict] = None

class TechStackRecommendation(BaseModel):
    """Recomendação completa de stack tecnológica."""
    frontend: dict = Field(..., description="Tecnologias frontend recomendadas")
    backend: dict = Field(..., description="Tecnologias backend recomendadas")
    authentication: dict = Field(..., description="Solução de autenticação")
    database: dict = Field(..., description="Sistema de banco de dados")
    llm: dict = Field(..., description="Integração com LLM")
    reasoning: str = Field(..., description="Explicação das escolhas") 