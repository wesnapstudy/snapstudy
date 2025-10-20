"""Authentication service using AWS Cognito."""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import hmac
import base64

from ..config import settings
from ..models.user import UserRegistration, UserLogin, AuthToken


class AuthService:
    """Service for user authentication using AWS Cognito."""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=settings.aws_region)
        self.user_pool_id = settings.user_pool_id
        self.client_id = settings.user_pool_client_id
    
    def _calculate_secret_hash(self, username: str) -> str:
        """Calculate secret hash for Cognito client."""
        # This is only needed if the client has a secret
        # For now, we'll assume no secret is configured
        return ""
    
    async def register_user(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register a new user with Cognito."""
        try:
            # Create user in Cognito
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=registration.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': registration.email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'name', 'Value': registration.full_name},
                ],
                TemporaryPassword=registration.password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Set permanent password
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=registration.email,
                Password=registration.password,
                Permanent=True
            )
            
            user_id = response['User']['Username']
            
            return {
                'user_id': user_id,
                'email': registration.email,
                'full_name': registration.full_name,
                'status': 'confirmed'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                raise ValueError("User with this email already exists")
            elif error_code == 'InvalidPasswordException':
                raise ValueError("Password does not meet requirements")
            else:
                raise ValueError(f"Registration failed: {e.response['Error']['Message']}")
    
    async def authenticate_user(self, login: UserLogin) -> AuthToken:
        """Authenticate user and return JWT token."""
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': login.email,
                    'PASSWORD': login.password
                }
            )
            
            # Get user details
            user_response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=login.email
            )
            
            user_id = user_response['Username']
            
            # Create custom JWT token
            token_data = {
                'user_id': user_id,
                'email': login.email,
                'exp': datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
                'iat': datetime.utcnow()
            }
            
            access_token = jwt.encode(
                token_data,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm
            )
            
            return AuthToken(
                access_token=access_token,
                expires_in=settings.jwt_expiration_hours * 3600,
                user_id=user_id
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
                raise ValueError("Invalid email or password")
            else:
                raise ValueError(f"Authentication failed: {e.response['Error']['Message']}")
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user data."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Cognito."""
        try:
            response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=user_id
            )
            
            # Parse user attributes
            attributes = {}
            for attr in response.get('UserAttributes', []):
                attributes[attr['Name']] = attr['Value']
            
            return {
                'user_id': response['Username'],
                'email': attributes.get('email'),
                'full_name': attributes.get('name'),
                'email_verified': attributes.get('email_verified') == 'true',
                'status': response.get('UserStatus'),
                'created_at': response.get('UserCreateDate'),
                'updated_at': response.get('UserLastModifiedDate')
            }
            
        except ClientError as e:
            raise ValueError(f"Failed to get user info: {e.response['Error']['Message']}")
    
    async def update_user_attributes(self, user_id: str, attributes: Dict[str, str]) -> bool:
        """Update user attributes in Cognito."""
        try:
            user_attributes = []
            for key, value in attributes.items():
                if key in ['profession', 'education_level', 'country', 'learning_style', 'attention_span', 'difficulty_level']:
                    user_attributes.append({
                        'Name': f'custom:{key}',
                        'Value': str(value)
                    })
                elif key == 'full_name':
                    user_attributes.append({
                        'Name': 'name',
                        'Value': value
                    })
            
            if user_attributes:
                self.cognito_client.admin_update_user_attributes(
                    UserPoolId=self.user_pool_id,
                    Username=user_id,
                    UserAttributes=user_attributes
                )
            
            return True
            
        except ClientError as e:
            raise ValueError(f"Failed to update user attributes: {e.response['Error']['Message']}")
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # First authenticate with old password
            self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': user_id,
                    'PASSWORD': old_password
                }
            )
            
            # Set new password
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=user_id,
                Password=new_password,
                Permanent=True
            )
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise ValueError("Current password is incorrect")
            elif error_code == 'InvalidPasswordException':
                raise ValueError("New password does not meet requirements")
            else:
                raise ValueError(f"Password change failed: {e.response['Error']['Message']}")


# Global service instance
auth_service = AuthService()