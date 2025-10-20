"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt
import hashlib
import uuid
from datetime import datetime, timedelta

from ...models.user import UserRegistration, UserLogin, AuthToken

router = APIRouter()
security = HTTPBearer()

# Simple in-memory user store for demo (replace with real database)
users_db = {}
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[user_id]

@router.post("/register", response_model=Dict[str, Any])
async def register_user(registration: UserRegistration):
    """Register a new user."""
    try:
        # Check if user already exists
        for user in users_db.values():
            if user["email"] == registration.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
        
        # Create new user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "user_id": user_id,
            "email": registration.email,
            "password_hash": hash_password(registration.password),
            "username": registration.full_name.split()[0] if registration.full_name else "",
            "first_name": registration.full_name.split()[0] if registration.full_name else "",
            "last_name": " ".join(registration.full_name.split()[1:]) if len(registration.full_name.split()) > 1 else "",
            "full_name": registration.full_name,
            "profession": registration.profession,
            "education_level": registration.education_level,
            "country": registration.country,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        users_db[user_id] = user_data
        
        # Create access token
        access_token = create_access_token(user_id, registration.email)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": registration.email,
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Dict[str, Any])
async def login_user(login: UserLogin):
    """Authenticate user and return access token."""
    try:
        # Find user by email
        user = None
        for u in users_db.values():
            if u["email"] == login.email:
                user = u
                break
        
        if not user or not verify_password(login.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(user["user_id"], user["email"])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["user_id"],
                "email": user["email"],
                "username": user["username"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
        }
        
    except HTTPException:
        raise
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
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user["user_id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"]
    }