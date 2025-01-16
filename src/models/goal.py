from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GoalTimeframe(str, Enum):
    """Enum para prazo de objetivos."""
    SHORT_TERM = "short_term"  # < 3 meses
    MEDIUM_TERM = "medium_term"  # 3-12 meses
    LONG_TERM = "long_term"  # > 12 meses

class GoalStatus(str, Enum):
    """Enum para status de objetivos."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"

class GoalCategory(str, Enum):
    """Enum para categorias de objetivos."""
    CAREER = "career"
    EDUCATION = "education"
    HEALTH = "health"
    FINANCE = "finance"
    PERSONAL = "personal"
    RELATIONSHIPS = "relationships"
    OTHER = "other"

class GoalBase(BaseModel):
    """Modelo base para objetivos."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: GoalCategory = Field(default=GoalCategory.OTHER)
    timeframe: GoalTimeframe = Field(default=GoalTimeframe.MEDIUM_TERM)
    target_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

class GoalCreate(GoalBase):
    """Modelo para criação de objetivos."""
    user_id: str

class Goal(GoalBase):
    """Modelo completo de objetivos."""
    id: str
    user_id: str
    status: GoalStatus = Field(default=GoalStatus.PLANNED)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    achieved_at: Optional[datetime] = None
    related_tasks: List[str] = Field(default_factory=list)  # Lista de IDs de tarefas
    
    class Config:
        from_attributes = True

class GoalUpdate(BaseModel):
    """Modelo para atualização de objetivos."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[GoalCategory] = None
    timeframe: Optional[GoalTimeframe] = None
    status: Optional[GoalStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    target_date: Optional[datetime] = None
    tags: Optional[List[str]] = None 