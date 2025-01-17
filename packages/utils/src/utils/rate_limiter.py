from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import Request

class RateLimiter:
    def __init__(self, max_requests: int, time_window: timedelta):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}

    async def check_rate_limit(self, request: Request, user_id: str):
        current_time = datetime.now()
        
        # Limpa requisições antigas
        self.requests[user_id] = [
            t for t in self.requests.get(user_id, []) 
            if current_time - t < self.time_window
        ]
        
        # Verifica se excedeu o limite
        if len(self.requests[user_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {self.time_window.total_seconds()} seconds"
            )
        
        # Adiciona nova requisição
        self.requests[user_id].append(current_time)

# Configuração recomendada para LLMs
# 30 requisições por minuto por utilizador
rate_limiter = RateLimiter(
    max_requests=30,
    time_window=timedelta(minutes=1)
) 