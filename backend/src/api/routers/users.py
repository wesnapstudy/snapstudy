"""Users router."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/me")
async def get_current_user():
    return {"message": "Get current user - implementation needed"}