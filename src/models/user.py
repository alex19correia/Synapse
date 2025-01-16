from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Modelo base para utilizador."""
    email: EmailStr
    name: str
    
class UserCreate(UserBase):
    """Modelo para criação de utilizador."""
    pass

class UserPreferences(BaseModel):
    """Preferências do utilizador."""
    default_llm_provider: Optional[str] = Field(None, description="Provedor LLM preferido")
    default_llm_model: Optional[str] = Field(None, description="Modelo LLM preferido")
    temperature: float = Field(0.7, ge=0, le=1, description="Temperatura para geração de texto")
    language: str = Field("pt-PT", description="Idioma preferido")
    theme: str = Field("light", description="Tema da interface")

class User(UserBase):
    """Modelo completo de utilizador."""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    class Config:
        from_attributes = True 