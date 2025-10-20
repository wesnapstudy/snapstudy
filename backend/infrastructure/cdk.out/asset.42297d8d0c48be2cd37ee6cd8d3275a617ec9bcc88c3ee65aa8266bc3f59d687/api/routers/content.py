"""Content processing API endpoints."""

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import Dict, Any

from ...models.lesson import ContentType, ProcessingStatus
from ...services.dynamodb import db_service

router = APIRouter()

@router.post("/upload")
async def upload_content(
    user_id: str,
    title: str,
    description: str = None,
    content_type: str = "pdf",
    file: UploadFile = File(None),
    url: str = None
):
    """Upload content for processing."""
    try:
        # Validate content type
        if content_type not in [ct.value for ct in ContentType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type"
            )
        
        # Validate input
        if not file and not url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file or URL must be provided"
            )
        
        if content_type == "youtube" and not url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL is required for YouTube content"
            )
        
        # Create lesson record
        lesson_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "processing_status": ProcessingStatus.PENDING.value,
            "status": "draft"
        }
        
        if url:
            lesson_data["original_content_url"] = url
        
        if file:
            # TODO: Upload file to S3 and store the key
            lesson_data["s3_content_key"] = f"uploads/{user_id}/{file.filename}"
        
        lesson = await db_service.create_lesson(lesson_data)
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "content_uploaded",
            "event_data": {
                "lesson_id": lesson["lesson_id"],
                "content_type": content_type,
                "title": title,
                "has_file": file is not None,
                "has_url": url is not None
            }
        })
        
        # TODO: Trigger content processing workflow (Step Functions)
        
        return {
            "message": "Content uploaded successfully",
            "lesson_id": lesson["lesson_id"],
            "processing_status": "pending",
            "estimated_processing_time": "5-10 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload content"
        )

@router.get("/processing-status/{lesson_id}")
async def get_processing_status(lesson_id: str):
    """Get content processing status."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        processing_status = lesson.get("processing_status", "unknown")
        
        status_info = {
            "lesson_id": lesson_id,
            "processing_status": processing_status,
            "title": lesson.get("title"),
            "content_type": lesson.get("content_type"),
            "created_at": lesson.get("created_at"),
            "updated_at": lesson.get("updated_at")
        }
        
        # Add progress information based on status
        if processing_status == ProcessingStatus.PENDING.value:
            status_info["message"] = "Content is queued for processing"
            status_info["progress_percentage"] = 0
        elif processing_status == ProcessingStatus.PROCESSING.value:
            status_info["message"] = "Content is being processed"
            status_info["progress_percentage"] = 50
        elif processing_status == ProcessingStatus.COMPLETED.value:
            status_info["message"] = "Content processing completed"
            status_info["progress_percentage"] = 100
            
            # Get micro-lessons count
            micro_lessons = await db_service.get_lesson_micro_lessons(lesson_id)
            status_info["micro_lessons_generated"] = len(micro_lessons)
        elif processing_status == ProcessingStatus.FAILED.value:
            status_info["message"] = "Content processing failed"
            status_info["progress_percentage"] = 0
            status_info["error"] = lesson.get("processing_error", "Unknown error")
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processing status"
        )

@router.post("/reprocess/{lesson_id}")
async def reprocess_content(lesson_id: str):
    """Reprocess failed content."""
    try:
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        current_status = lesson.get("processing_status")
        if current_status not in [ProcessingStatus.FAILED.value, ProcessingStatus.COMPLETED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content can only be reprocessed if it failed or completed"
            )
        
        # Reset processing status
        await db_service.update_lesson(lesson_id, {
            "processing_status": ProcessingStatus.PENDING.value,
            "processing_error": None
        })
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": lesson["user_id"],
            "event_type": "content_reprocessed",
            "event_data": {
                "lesson_id": lesson_id,
                "previous_status": current_status
            }
        })
        
        # TODO: Trigger content processing workflow again
        
        return {
            "message": "Content reprocessing initiated",
            "lesson_id": lesson_id,
            "processing_status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reprocess content"
        )

@router.delete("/{lesson_id}")
async def delete_content(lesson_id: str, user_id: str):
    """Delete content and associated lesson."""
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
        
        # TODO: Delete from S3 if file exists
        # TODO: Delete micro-lessons and quizzes
        # TODO: Implement soft delete or archive instead of hard delete
        
        # Track engagement
        await db_service.track_engagement({
            "user_id": user_id,
            "event_type": "content_deleted",
            "event_data": {
                "lesson_id": lesson_id,
                "title": lesson.get("title"),
                "content_type": lesson.get("content_type")
            }
        })
        
        return {
            "message": "Content deletion initiated",
            "lesson_id": lesson_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )