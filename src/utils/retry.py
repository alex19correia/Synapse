import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any
from loguru import logger

T = TypeVar('T')

def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    exponential_backoff: bool = True,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorador para adicionar retry a funções assíncronas.
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Tempo de espera entre tentativas (segundos)
        exponential_backoff: Se True, aumenta o tempo de espera exponencialmente
        exceptions: Tupla de exceções que devem trigger retry
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Falha após {max_retries} tentativas: {str(e)}")
                        raise
                    
                    logger.warning(
                        f"Tentativa {retries} falhou, tentando novamente em {current_delay}s"
                    )
                    
                    await asyncio.sleep(current_delay)
                    
                    if exponential_backoff:
                        current_delay *= 2
            
            return None
        
        return wrapper
    return decorator 