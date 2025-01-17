from pydantic import BaseModel
from typing import Dict, Any, Optional

class LLMMetric(BaseModel):
    model: str
    duration: float
    tokens: int
    success: bool

class CacheMetric(BaseModel):
    operation_type: str
    hit: bool

class UserMetric(BaseModel):
    user_id: str
    session_duration: float

class ErrorMetric(BaseModel):
    error_type: str
    component: str

class LogMetric(BaseModel):
    level: str
    component: str
    hasError: bool
    metadata: Optional[Dict[str, Any]] = None

class ApiMetric(BaseModel):
    path: str
    method: str
    statusCode: int
    duration: float

class DurationMetric(BaseModel):
    component: str
    duration: float

class MemoryMetric(BaseModel):
    component: str
    usage: float 