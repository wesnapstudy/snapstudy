"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from ...models.user import UserRegistration, UserLogin, AuthToken
from ...services.auth import auth_service
from ...services.dynamodb import db_service

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
async def register_user(registration: UserRegistration):
    """Register a new user."""
    try:
        # Check if user already exists in our database
        existing_user = await db_service.get_user_by_email(registration.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Register with Cognito
        cognito_user = await auth_service.register_user(registration)
        
        # Create user in our database
        user_data = {
            'email': registration.email,
            'full_name': registration.full_name,
            'profession': registration.profession,
            'education_level': registration.education_level,
            'country': registration.country,
            'is_active': True
        }
        
        # Use the Cognito user ID
        user_data['user_id'] = cognito_user['user_id']
        db_user = await db_service.create_user(user_data)
        
        return {
            "message": "User registered successfully",
            "user_id": db_user['user_id'],
            "email": db_user['email']
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthToken)
async def login_user(login: UserLogin):
    """Authenticate user and return access token."""
    try:
        # Authenticate with Cognito
        token = await auth_service.authenticate_user(login)
        
        # Track login engagement
        user = await db_service.get_user_by_email(login.email)
        if user:
            await db_service.track_engagement({
                'user_id': user['user_id'],
                'event_type': 'login',
                'event_data': {'email': login.email}
            })
        
        return token
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/logout")
async def logout_user():
    """Logout user (client-side token removal)."""
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = None):
    """Get current user information."""
    # This would use the get_current_user dependency from main.py
    return {
        "user_id": current_user['user_id'],
        "email": current_user['email'],
        "full_name": current_user['full_name'],
        "is_active": current_user['is_active']
    }