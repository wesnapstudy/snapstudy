"""Main FastAPI application for SnapStudy backend."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
import logging

from ..config import settings
from ..services.auth import auth_service
from ..services.dynamodb import db_service
from .routers import auth, users, lessons, content, ai_services, adaptive, quiz, chat, analytics, multimedia

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SnapStudy API",
    description="Backend API for SnapStudy adaptive learning platform",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user."""
    # Import here to avoid circular imports
    from .routers.auth import verify_token, users_db
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        if not user_id or user_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return users_db[user_id]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["Lessons"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(ai_services.router, prefix="/api/v1/ai", tags=["AI Services"])
app.include_router(adaptive.router, prefix="/api/v1/adaptive", tags=["Adaptive Learning"])
app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["Quiz System"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Agentic Chat"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Learning Analytics"])
app.include_router(multimedia.router, prefix="/api/v1/multimedia", tags=["Multimedia Generation"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SnapStudy API",
        "version": settings.api_version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Lambda handler
handler = Mangum(app)