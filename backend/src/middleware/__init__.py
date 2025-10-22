# Middleware package

from .auth_middleware import (
    AuthenticationMiddleware,
    EnhancedHTTPBearer,
    RequireAuth,
    require_auth,
    require_auth_with_onboarding,
    enhanced_bearer
)
from .security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    JWTValidator,
    CORSSecurityMiddleware,
    jwt_validator
)
from .error_handler import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError,
    RateLimitError,
    create_error_response
)

__all__ = [
    # Authentication middleware
    'AuthenticationMiddleware',
    'EnhancedHTTPBearer', 
    'RequireAuth',
    'require_auth',
    'require_auth_with_onboarding',
    'enhanced_bearer',
    
    # Security middleware
    'SecurityHeadersMiddleware',
    'RateLimitMiddleware',
    'RequestLoggingMiddleware',
    'JWTValidator',
    'CORSSecurityMiddleware',
    'jwt_validator',
    
    # Error handling
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'ResourceNotFoundError',
    'ResourceConflictError',
    'RateLimitError',
    'create_error_response'
]