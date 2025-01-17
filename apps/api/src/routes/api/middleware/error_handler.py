"""Error handling middleware."""
from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from rich.console import Console

console = Console()

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            FastAPI response
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            console.print(f"[error]HTTP error: {e.detail}[/error]")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            console.print(f"[error]Internal error: {str(e)}[/error]")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Internal server error: {str(e)}"}
            )
