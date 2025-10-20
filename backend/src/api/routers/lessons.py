"""Lessons router."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_lessons():
    return {"message": "Get lessons - implementation needed"}