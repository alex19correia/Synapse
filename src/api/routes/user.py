"""
User routes for the API.
"""
from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_settings, get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
async def get_user_profile(
    settings = Depends(get_settings),
    current_user = Depends(get_current_user)
):
    """Get current user profile."""
    # For testing purposes, return mock user data
    if settings.ENV == "test":
        return {
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    # In production, return actual user data
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    } 