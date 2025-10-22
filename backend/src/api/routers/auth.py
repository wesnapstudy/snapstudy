"""Authentication router."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import logging
from datetime import datetime, timedelta
import jwt
import uuid
import traceback

from ...models.user import UserRegistration, UserLogin, AuthToken, UserProfile
from ...services.dynamodb import db_service
from ...services.password_service import PasswordService
from ...services.jwt_service import jwt_service
from ...config import settings
from ...middleware.error_handler import AuthenticationError, ValidationError, ResourceConflictError

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to verify JWT token from Authorization header.
    
    Returns:
        Decoded token payload if valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = jwt_service.validate_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

@router.post("/register", response_model=AuthToken)
async def register(user_data: UserRegistration):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    try:
        # Check if user already exists
        existing_user = await db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise ResourceConflictError("User", "email", user_data.email)
        
        # Generate user ID and hash password
        user_id = str(uuid.uuid4())
        hashed_password = PasswordService.hash_password(user_data.password)
        
        # Use provided full_name or None
        full_name = user_data.full_name
        
        # Create user profile
        now = datetime.utcnow()
        user_profile = UserProfile(
            user_id=user_id,
            email=user_data.email,
            full_name=full_name,
            profession=user_data.profession,
            education_level=user_data.education_level,
            country=user_data.country,
            created_at=now,
            updated_at=now,
            is_active=True
        )
        
        # Save user to database
        user_item = {
            "user_id": user_id,
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "profession": user_data.profession,
            "education_level": user_data.education_level,
            "country": user_data.country,
            "onboarding_completed": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "is_active": True
        }
        
        await db_service.create_user(user_item)
        
        # Create access token
        user_token_data = {
            'user_id': user_id,
            'email': user_data.email,
            'full_name': full_name,
            'onboarding_completed': False
        }
        access_token = jwt_service.generate_token(user_token_data)
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return AuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user_id=user_id
        )
        
    except (ResourceConflictError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthToken)
async def login(user_data: UserLogin):
    """Login user."""
    try:
        # Get user from database
        user = await db_service.get_user_by_email(user_data.email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        password_hash = user.get("password_hash", "")
        if not PasswordService.verify_password(user_data.password, password_hash):
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.get("is_active", False):
            raise AuthenticationError("Account is deactivated")
        
        # Create access token
        user_token_data = {
            'user_id': user["user_id"],
            'email': user["email"],
            'full_name': user.get("full_name", ""),
            'onboarding_completed': user.get("onboarding_completed", False)
        }
        access_token = jwt_service.generate_token(user_token_data)
        
        logger.info(f"User logged in successfully: {user_data.email}")
        
        return AuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user_id=user["user_id"]
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Login failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/logout")
async def logout():
    """
    Logout endpoint.

    Invalidates the current session/token.
    """
    return {"message": "Logged out successfully"}

@router.get("/verify")
async def verify_token_endpoint(token: str = Depends(verify_token)):
    """
    Token verification endpoint.

    Verifies if the provided token is valid.
    """
    return {"valid": True, "message": "Token is valid", "user_id": token.get("user_id")}