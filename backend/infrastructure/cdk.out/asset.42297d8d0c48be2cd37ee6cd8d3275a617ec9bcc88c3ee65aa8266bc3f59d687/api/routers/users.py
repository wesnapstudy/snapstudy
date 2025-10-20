"""User management API endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any

from ...models.user import UserProfileUpdate, UserPreferences
from ...services.dynamodb import db_service
from ...services.auth import auth_service

router = APIRouter()

@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by ID."""
    try:
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "profession": user.get("profession"),
            "education_level": user.get("education_level"),
            "country": user.get("country"),
            "learning_style": user.get("learning_style"),
            "attention_span": user.get("attention_span"),
            "difficulty_level": user.get("difficulty_level"),
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "is_active": user.get("is_active", True)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

@router.put("/{user_id}")
async def update_user_profile(user_id: str, profile_update: UserProfileUpdate):
    """Update user profile."""
    try:
        # Check if user exists
        existing_user = await db_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {}
        if profile_update.full_name is not None:
            update_data["full_name"] = profile_update.full_name
        if profile_update.profession is not None:
            update_data["profession"] = profile_update.profession
        if profile_update.education_level is not None:
            update_data["education_level"] = profile_update.education_level
        if profile_update.country is not None:
            update_data["country"] = profile_update.country
        if profile_update.learning_style is not None:
            update_data["learning_style"] = profile_update.learning_style.value
        if profile_update.attention_span is not None:
            update_data["attention_span"] = profile_update.attention_span
        if profile_update.difficulty_level is not None:
            update_data["difficulty_level"] = profile_update.difficulty_level.value
        
        # Update in DynamoDB
        updated_user = await db_service.update_user(user_id, update_data)
        
        # Update Cognito attributes if needed
        cognito_attributes = {}
        if profile_update.full_name is not None:
            cognito_attributes["full_name"] = profile_update.full_name
        if profile_update.profession is not None:
            cognito_attributes["profession"] = profile_update.profession
        if profile_update.education_level is not None:
            cognito_attributes["education_level"] = profile_update.education_level
        if profile_update.country is not None:
            cognito_attributes["country"] = profile_update.country
        if profile_update.learning_style is not None:
            cognito_attributes["learning_style"] = profile_update.learning_style.value
        if profile_update.attention_span is not None:
            cognito_attributes["attention_span"] = str(profile_update.attention_span)
        if profile_update.difficulty_level is not None:
            cognito_attributes["difficulty_level"] = profile_update.difficulty_level.value
        
        if cognito_attributes:
            await auth_service.update_user_attributes(user_id, cognito_attributes)
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "profile_update",
            "event_data": {"updated_fields": list(update_data.keys())}
        })
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/{user_id}/preferences")
async def set_user_preferences(user_id: str, preferences: UserPreferences):
    """Set user learning preferences."""
    try:
        # Check if user exists
        existing_user = await db_service.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update preferences
        update_data = {
            "learning_style": preferences.learning_style.value,
            "attention_span": preferences.attention_span,
            "difficulty_level": preferences.difficulty_level.value,
            "interests": preferences.interests,
            "goals": preferences.goals
        }
        
        updated_user = await db_service.update_user(user_id, update_data)
        
        # Update Cognito custom attributes
        cognito_attributes = {
            "learning_style": preferences.learning_style.value,
            "attention_span": str(preferences.attention_span),
            "difficulty_level": preferences.difficulty_level.value
        }
        await auth_service.update_user_attributes(user_id, cognito_attributes)
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "preferences_set",
            "event_data": {
                "learning_style": preferences.learning_style.value,
                "attention_span": preferences.attention_span,
                "difficulty_level": preferences.difficulty_level.value
            }
        })
        
        return {
            "message": "Preferences updated successfully",
            "preferences": {
                "learning_style": preferences.learning_style.value,
                "attention_span": preferences.attention_span,
                "difficulty_level": preferences.difficulty_level.value,
                "interests": preferences.interests,
                "goals": preferences.goals
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@router.get("/{user_id}/engagement")
async def get_user_engagement(user_id: str, limit: int = 50):
    """Get user engagement history."""
    try:
        engagement_data = await db_service.get_user_engagement(user_id, limit)
        
        return {
            "user_id": user_id,
            "engagement_history": engagement_data,
            "total_events": len(engagement_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve engagement data"
        )