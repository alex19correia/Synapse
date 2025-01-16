"""Health check routes."""
from fastapi import APIRouter, status

router = APIRouter()

@router.get(
    "/health",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
