from typing import Callable, TypeVar, Any
from functools import wraps
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class CircuitBreakerState(BaseModel):
    failures: int = 0
    last_failure: datetime | None = None
    is_open: bool = False
    next_attempt: datetime | None = None

class ResilienceConfig(BaseModel):
    max_retries: int = 3
    retry_delay: float = 1.0  # segundos
    circuit_threshold: int = 5  # falhas
    reset_timeout: int = 60  # segundos

class Resilience:
    """Gerencia retry e circuit breaker para chamadas externas"""
    
    def __init__(self):
        self.config = ResilienceConfig()
        self.states: dict[str, CircuitBreakerState] = {}

    def _get_state(self, key: str) -> CircuitBreakerState:
        if key not in self.states:
            self.states[key] = CircuitBreakerState()
        return self.states[key]

    def with_resilience(self, key: str):
        """Decorator para adicionar retry e circuit breaker"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                state = self._get_state(key)

                # Verifica circuit breaker
                if state.is_open:
                    if datetime.now() < state.next_attempt:
                        raise Exception(f"Circuit breaker aberto para {key}")
                    state.is_open = False

                # Tenta executar com retry
                for attempt in range(self.config.max_retries):
                    try:
                        result = await func(*args, **kwargs)
                        # Reseta estado em caso de sucesso
                        state.failures = 0
                        state.last_failure = None
                        return result
                    except Exception as e:
                        state.failures += 1
                        state.last_failure = datetime.now()
                        
                        # Verifica se deve abrir circuit breaker
                        if state.failures >= self.config.circuit_threshold:
                            state.is_open = True
                            state.next_attempt = datetime.now() + timedelta(
                                seconds=self.config.reset_timeout
                            )
                            logger.warning(f"Circuit breaker aberto para {key}")
                            raise Exception(f"Circuit breaker aberto após {state.failures} falhas")

                        # Retry delay
                        if attempt < self.config.max_retries - 1:
                            delay = self.config.retry_delay * (2 ** attempt)  # exponential backoff
                            logger.info(f"Tentativa {attempt + 1} falhou, aguardando {delay}s")
                            await asyncio.sleep(delay)
                        else:
                            raise e

            return wrapper
        return decorator

# Instância global
resilience = Resilience() 