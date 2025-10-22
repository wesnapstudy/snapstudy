"""
Password hashing service for secure password management.

Provides SHA-256 password hashing with random salt generation,
password verification, and password strength validation.
"""

import hashlib
import secrets
import re
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PasswordService:
    """Service for secure password hashing and validation."""

    @staticmethod
    def generate_salt() -> str:
        """
        Generate a random salt for password hashing.
        
        Returns:
            Random salt as hex string
        """
        return secrets.token_hex(32)  # 64 character hex string (32 bytes)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash password using SHA-256 with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (generates new one if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = PasswordService.generate_salt()
        
        # Combine password and salt
        salted_password = password + salt
        
        # Hash using SHA-256
        password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        
        logger.debug("Password hashed successfully")
        return password_hash, salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify password against stored hash and salt.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored password hash
            salt: Salt used for original hash
            
        Returns:
            True if password matches, False otherwise
        """
        # Hash the provided password with the stored salt
        computed_hash, _ = PasswordService.hash_password(password, salt)
        
        # Compare hashes using constant-time comparison to prevent timing attacks
        return secrets.compare_digest(computed_hash, stored_hash)

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength according to security requirements.
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        
        Args:
            password: Password to validate
            
        Returns:
            Dict with validation result and details
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'requirements_met': {
                'min_length': False,
                'has_uppercase': False,
                'has_lowercase': False,
                'has_digit': False,
                'has_special': False
            }
        }
        
        # Check minimum length
        if len(password) >= 8:
            validation_result['requirements_met']['min_length'] = True
        else:
            validation_result['errors'].append("Password must be at least 8 characters long")
            validation_result['is_valid'] = False
        
        # Check for uppercase letter
        if re.search(r'[A-Z]', password):
            validation_result['requirements_met']['has_uppercase'] = True
        else:
            validation_result['errors'].append("Password must contain at least one uppercase letter")
            validation_result['is_valid'] = False
        
        # Check for lowercase letter
        if re.search(r'[a-z]', password):
            validation_result['requirements_met']['has_lowercase'] = True
        else:
            validation_result['errors'].append("Password must contain at least one lowercase letter")
            validation_result['is_valid'] = False
        
        # Check for digit
        if re.search(r'\d', password):
            validation_result['requirements_met']['has_digit'] = True
        else:
            validation_result['errors'].append("Password must contain at least one digit")
            validation_result['is_valid'] = False
        
        # Check for special character
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            validation_result['requirements_met']['has_special'] = True
        else:
            validation_result['errors'].append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
            validation_result['is_valid'] = False
        
        logger.debug(f"Password validation completed: {'valid' if validation_result['is_valid'] else 'invalid'}")
        return validation_result


# Global service instance
password_service = PasswordService()