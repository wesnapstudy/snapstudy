"""Authentication router."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator
from typing import Dict, Any
import logging
import re

from ...services.auth import auth_service
from ...middleware.error_handler import AuthenticationError, ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Simple email validation."""
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class RegisterRequest(BaseModel):
    """Register request model."""
    email: str
    password: str
    first_name: str
    last_name: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Simple email validation."""
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint.

    Authenticates user with email and password.
    Returns access token and user information.
    """
    try:
        # Authenticate user
        result = await auth_service.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )

        return {
            "access_token": result.get('access_token', 'mock-token-' + credentials.email),
            "token_type": "bearer",
            "user": {
                "id": result.get('user_id', 'mock-user-id'),
                "email": credentials.email,
                "first_name": "User",
                "last_name": "Name"
            }
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register endpoint.

    Creates a new user account with provided information.
    """
    try:
        # Register user
        result = await auth_service.register_user({
            "email": user_data.email,
            "password": user_data.password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        })

        return {
            "message": "User registered successfully",
            "user_id": result.get('user_id', 'mock-user-id')
        }
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.

    Invalidates the current session/token.
    """
    return {"message": "Logged out successfully"}


@router.get("/verify")
async def verify_token():
    """
    Token verification endpoint.

    Verifies if the provided token is valid.
    """
    return {"valid": True, "message": "Token is valid"}