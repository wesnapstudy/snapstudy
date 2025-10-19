"""User data models."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING = "reading"
    KINESTHETIC = "kinesthetic"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserProfile(BaseModel):
    """User profile data model."""
    user_id: str
    email: EmailStr
    full_name: str
    profession: Optional[str] = None
    education_level: Optional[str] = None
    country: Optional[str] = None
    learning_style: Optional[LearningStyle] = None
    attention_span: Optional[int] = Field(None, ge=5, le=60)  # minutes
    difficulty_level: Optional[DifficultyLevel] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class UserRegistration(BaseModel):
    """User registration request model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
    profession: Optional[str] = None
    education_level: Optional[str] = None
    country: Optional[str] = None


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """User profile update model."""
    full_name: Optional[str] = None
    profession: Optional[str] = None
    education_level: Optional[str] = None
    country: Optional[str] = None
    learning_style: Optional[LearningStyle] = None
    attention_span: Optional[int] = Field(None, ge=5, le=60)
    difficulty_level: Optional[DifficultyLevel] = None


class UserPreferences(BaseModel):
    """User learning preferences model."""
    learning_style: LearningStyle
    attention_span: int = Field(..., ge=5, le=60)
    difficulty_level: DifficultyLevel
    interests: list[str] = []
    goals: list[str] = []


class AuthToken(BaseModel):
    """Authentication token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str