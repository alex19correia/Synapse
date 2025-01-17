from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    """Enum para prioridade de tarefas."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    """Enum para status de tarefas."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    """Modelo base para tarefas."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

class TaskCreate(TaskBase):
    """Modelo para criação de tarefas."""
    user_id: str
    goal_id: Optional[str] = None

class Task(TaskBase):
    """Modelo completo de tarefas."""
    id: str
    user_id: str
    goal_id: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    """Modelo para atualização de tarefas."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    goal_id: Optional[str] = None 