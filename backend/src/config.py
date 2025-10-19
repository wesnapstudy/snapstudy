"""Configuration settings for SnapStudy backend."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_account_id: Optional[str] = os.getenv("AWS_ACCOUNT_ID")
    
    # DynamoDB Table Names
    users_table: str = os.getenv("USERS_TABLE", "SnapStudy-Users")
    lessons_table: str = os.getenv("LESSONS_TABLE", "SnapStudy-Lessons")
    micro_lessons_table: str = os.getenv("MICRO_LESSONS_TABLE", "SnapStudy-MicroLessons")
    quizzes_table: str = os.getenv("QUIZZES_TABLE", "SnapStudy-Quizzes")
    user_engagement_table: str = os.getenv("USER_ENGAGEMENT_TABLE", "SnapStudy-UserEngagement")
    chat_history_table: str = os.getenv("CHAT_HISTORY_TABLE", "SnapStudy-ChatHistory")
    
    # S3 Configuration
    content_bucket: str = os.getenv("CONTENT_BUCKET", f"snapstudy-content-{os.getenv('AWS_ACCOUNT_ID', '054037102331')}-{os.getenv('AWS_REGION', 'us-east-1')}")
    
    # Cognito Configuration
    user_pool_id: str = os.getenv("USER_POOL_ID", "")
    user_pool_client_id: str = os.getenv("USER_POOL_CLIENT_ID", "")
    
    # AI/ML Configuration
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    
    # Bedrock Agents Configuration
    bedrock_agent_id: Optional[str] = os.getenv("BEDROCK_AGENT_ID")
    bedrock_agent_alias_id: str = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
    bedrock_knowledge_base_id: Optional[str] = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID")
    
    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Configuration
    api_version: str = "v1"
    cors_origins: list = ["*"]  # TODO: Restrict in production
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()