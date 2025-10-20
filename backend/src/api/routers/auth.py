"""Authentication router."""

from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    """Login endpoint."""
    return {"message": "Login endpoint - implementation needed"}

@router.post("/register")
async def register():
    """Register endpoint."""
    return {"message": "Register endpoint - implementation needed"}