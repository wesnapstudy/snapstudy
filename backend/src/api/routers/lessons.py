"""Lesson management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from ...models.lesson import ContentUpload, LessonStatus, ProcessingStatus
from ...services.dynamodb import db_service

router = APIRouter()

@router.post("/")
async def create_lesson(lesson_data: ContentUpload, user_id: str):
    """Create a new lesson from uploaded content."""
    try:
        # Create lesson record
        lesson_record = {
            "user_id": user_id,
            "title": lesson_data.title,
            "description": lesson_data.description,
            "content_type": lesson_data.content_type.value,
            "original_content_url": lesson_data.file_url,
            "processing_status": ProcessingStatus.PENDING.value,
            "status": LessonStatus.DRAFT.value,
            "learning_objectives": lesson_data.learning_objectives or [],
            "total_micro_lessons": 0,
            "completed_micro_lessons": 0
        }
        
        lesson = await db_service.create_lesson(lesson_record)
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "lesson_created",
            "event_data": {
                "lesson_id": lesson["lesson_id"],
                "content_type": lesson_data.content_type.value,
                "title": lesson_data.title
            }
        })
        
        return {
            "message": "Lesson created successfully",
            "lesson_id": lesson["lesson_id"],
            "status": "pending_processing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lesson"
        )

@router.get("/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get lesson details by ID."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Get micro-lessons for this lesson
        micro_lessons = await db_service.get_lesson_micro_lessons(lesson_id)
        
        return {
            "lesson": lesson,
            "micro_lessons": micro_lessons,
            "total_micro_lessons": len(micro_lessons)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson"
        )

@router.get("/user/{user_id}")
async def get_user_lessons(user_id: str):
    """Get all lessons for a user."""
    try:
        lessons = await db_service.get_user_lessons(user_id)
        
        # Add progress information for each lesson
        lessons_with_progress = []
        for lesson in lessons:
            micro_lessons = await db_service.get_lesson_micro_lessons(lesson["lesson_id"])
            
            lesson_with_progress = {
                **lesson,
                "total_micro_lessons": len(micro_lessons),
                "completion_percentage": (
                    lesson.get("completed_micro_lessons", 0) / len(micro_lessons) * 100
                    if micro_lessons else 0
                )
            }
            lessons_with_progress.append(lesson_with_progress)
        
        return {
            "user_id": user_id,
            "lessons": lessons_with_progress,
            "total_lessons": len(lessons_with_progress)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user lessons"
        )

@router.put("/{lesson_id}/status")
async def update_lesson_status(lesson_id: str, status_data: Dict[str, str]):
    """Update lesson status."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        new_status = status_data.get("status")
        if new_status not in [s.value for s in LessonStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        updated_lesson = await db_service.update_lesson(lesson_id, {"status": new_status})
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": lesson["user_id"],
            "event_type": "lesson_status_updated",
            "event_data": {
                "lesson_id": lesson_id,
                "old_status": lesson.get("status"),
                "new_status": new_status
            }
        })
        
        return {
            "message": "Lesson status updated successfully",
            "lesson": updated_lesson
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lesson status"
        )

@router.get("/{lesson_id}/micro-lessons")
async def get_lesson_micro_lessons(lesson_id: str):
    """Get all micro-lessons for a lesson."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        micro_lessons = await db_service.get_lesson_micro_lessons(lesson_id)
        
        return {
            "lesson_id": lesson_id,
            "micro_lessons": micro_lessons,
            "total_count": len(micro_lessons)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve micro-lessons"
        )

@router.post("/{lesson_id}/start")
async def start_lesson(lesson_id: str, user_id: str):
    """Start a lesson for a user."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        if lesson["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update lesson status to active
        await db_service.update_lesson(lesson_id, {"status": LessonStatus.ACTIVE.value})
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "lesson_started",
            "event_data": {
                "lesson_id": lesson_id,
                "title": lesson.get("title")
            }
        })
        
        # Get first micro-lesson
        micro_lessons = await db_service.get_lesson_micro_lessons(lesson_id)
        first_micro_lesson = micro_lessons[0] if micro_lessons else None
        
        return {
            "message": "Lesson started successfully",
            "lesson_id": lesson_id,
            "current_micro_lesson": first_micro_lesson,
            "total_micro_lessons": len(micro_lessons)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start lesson"
        )