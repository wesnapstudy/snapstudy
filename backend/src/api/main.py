"""Main FastAPI application for SnapStudy backend."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from mangum import Mangum
import logging
import time
import uuid

from ..config import settings
from ..services.auth import auth_service
from ..services.dynamodb import db_service
from .routers import auth, users, lessons, content, ai_services, adaptive, quiz, chat, analytics, multimedia

# Import middleware and error handlers
from ..middleware.error_handler import (
    SnapStudyException,
    snapstudy_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from ..middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    CORSSecurityMiddleware,
    enhanced_bearer
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SnapStudy API",
    description="Backend API for SnapStudy adaptive learning platform with comprehensive error handling and security",
    version=settings.api_version,
    docs_url="/docs" if settings.api_version != "production" else None,
    redoc_url="/redoc" if settings.api_version != "production" else None
)

# Add exception handlers
app.add_exception_handler(SnapStudyException, snapstudy_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add security middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100, requests_per_hour=2000, burst_limit=20)
app.add_middleware(CORSSecurityMiddleware, allowed_origins=set(settings.cors_origins))

# Legacy CORS middleware for compatibility (will be overridden by CORSSecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced security with JWT validation
security = enhanced_bearer

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enhanced dependency to get current authenticated user with proper error handling."""
    from ..middleware.error_handler import AuthenticationError, ResourceNotFoundError
    
    if not credentials:
        raise AuthenticationError("Authentication required")
    
    try:
        # Get user ID from request state (set by enhanced_bearer)
        user_id = getattr(credentials, 'user_id', None)
        if hasattr(credentials, 'request') and hasattr(credentials.request.state, 'user_id'):
            user_id = credentials.request.state.user_id
        
        if not user_id:
            # Fallback to token parsing
            from ..middleware.security import jwt_validator
            payload = jwt_validator.verify_token(credentials.credentials)
            user_id = payload.get('user_id')
        
        if not user_id:
            raise AuthenticationError("Invalid token: user ID not found")
        
        # Get user from database
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)
        
        return user
        
    except (AuthenticationError, ResourceNotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise AuthenticationError(f"Authentication failed: {str(e)}")

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
    """Enhanced health check endpoint with system status."""
    from datetime import datetime
    import sys
    import os
    
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            db_service.health_check()
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check AWS services
        aws_status = "healthy"
        try:
            # Basic AWS connectivity check
            import boto3
            sts = boto3.client('sts')
            sts.get_caller_identity()
        except Exception as e:
            aws_status = f"unhealthy: {str(e)}"
        
        health_data = {
            "status": "healthy" if db_status == "healthy" and aws_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": settings.api_version,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "python_version": sys.version,
            "services": {
                "database": db_status,
                "aws": aws_status
            },
            "uptime_seconds": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    import time
    app.state.start_time = time.time()
    logger.info("SnapStudy API starting up...")
    
    # Initialize services
    try:
        db_service.initialize()
        logger.info("Database service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database service: {str(e)}")
    
    logger.info("SnapStudy API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("SnapStudy API shutting down...")
    
    # Cleanup resources
    try:
        db_service.cleanup()
        logger.info("Database service cleanup complete")
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
    
    logger.info("SnapStudy API shutdown complete")

# Lambda handler
handler = Mangum(app)