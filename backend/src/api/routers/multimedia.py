"""
Multimedia content generation API endpoints.

Handles audio and video micro-lesson generation requests.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...services.audio_generation import audio_generation_service
from ...services.video_generation import video_generation_service
from ...services.adaptive_agent import adaptive_learning_agent
from ...services.dynamodb import db_service
from ...auth.jwt_handler import get_current_user

router = APIRouter()


class AudioGenerationRequest(BaseModel):
    text_lesson_id: str
    voice_preference: Optional[str] = "professional_female"
    tone_preference: Optional[str] = "professional"
    speaking_rate: Optional[str] = "medium"
    audio_volume: Optional[str] = "medium"


class VideoGenerationRequest(BaseModel):
    text_lesson_id: str
    visual_style: Optional[str] = "educational"
    include_narration: Optional[bool] = True
    include_subtitles: Optional[bool] = True
    video_quality: Optional[str] = "hd"


class MultiModalGenerationRequest(BaseModel):
    lesson_content: str
    content_types: List[str] = ["text", "audio"]  # Can include "video"
    user_preferences: Optional[Dict[str, Any]] = {}


@router.post("/generate-audio")
async def generate_audio_lesson(
    request: AudioGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate audio micro-lesson from existing text lesson."""
    try:
        # Get text lesson
        text_lesson = await db_service.get_item('MicroLessons', {'micro_lesson_id': request.text_lesson_id})
        if not text_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Text lesson not found"
            )
        
        # Verify user owns the lesson
        if text_lesson.get('user_id') != current_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        # Build user profile with audio preferences
        user_profile = {
            **current_user,
            'voice_preference': request.voice_preference,
            'tone_preference': request.tone_preference,
            'speaking_rate': request.speaking_rate,
            'audio_volume': request.audio_volume
        }
        
        # Generate audio lesson
        audio_lesson = await audio_generation_service.generate_audio_micro_lesson(
            text_lesson, user_profile
        )
        
        return {
            "message": "Audio lesson generated successfully",
            "audio_lesson": audio_lesson,
            "generation_time": "2-5 minutes",
            "formats_available": ["mp3"],
            "features": [
                "Personalized voice selection",
                "Learning-optimized pacing",
                "Key concept emphasis",
                "Natural speech patterns"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audio lesson: {str(e)}"
        )


@router.post("/generate-video")
async def generate_video_lesson(
    request: VideoGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate video micro-lesson from existing text lesson."""
    try:
        # Get text lesson
        text_lesson = await db_service.get_item('MicroLessons', {'micro_lesson_id': request.text_lesson_id})
        if not text_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Text lesson not found"
            )
        
        # Verify user owns the lesson
        if text_lesson.get('user_id') != current_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        # Build user profile with video preferences
        user_profile = {
            **current_user,
            'visual_style_preference': request.visual_style,
            'include_narration': request.include_narration,
            'include_subtitles': request.include_subtitles,
            'video_quality': request.video_quality
        }
        
        # Generate video lesson
        video_lesson = await video_generation_service.generate_video_micro_lesson(
            text_lesson, user_profile
        )
        
        return {
            "message": "Video lesson generated successfully",
            "video_lesson": video_lesson,
            "generation_time": "5-15 minutes",
            "formats_available": ["mp4"],
            "features": [
                "AI-generated visuals",
                "Professional narration",
                "Interactive elements",
                "Learning-optimized pacing",
                "Accessibility features"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video lesson: {str(e)}"
        )


@router.post("/generate-multimodal")
async def generate_multimodal_lesson(
    request: MultiModalGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate micro-lesson in multiple formats simultaneously."""
    try:
        # Validate content types
        valid_types = ['text', 'audio', 'video']
        invalid_types = [t for t in request.content_types if t not in valid_types]
        if invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content types: {invalid_types}. Valid types: {valid_types}"
            )
        
        # Build user profile
        user_profile = {
            **current_user,
            **request.user_preferences
        }
        
        # Generate multi-modal lesson
        lesson_results = await adaptive_learning_agent.generate_multi_modal_micro_lesson(
            lesson_content=request.lesson_content,
            user_profile=user_profile,
            sequence_number=1,
            total_lessons=1,
            content_types=request.content_types
        )
        
        # Build response
        response = {
            "message": "Multi-modal lesson generated successfully",
            "lesson_id": lesson_results['lesson_id'],
            "generated_formats": lesson_results['generated_formats'],
            "success_rate": len(lesson_results['generated_formats']) / len(request.content_types),
            "lessons": {}
        }
        
        # Add generated lessons to response
        if 'text_lesson' in lesson_results:
            response['lessons']['text'] = lesson_results['text_lesson']
        
        if 'audio_lesson' in lesson_results:
            response['lessons']['audio'] = lesson_results['audio_lesson']
        
        if 'video_lesson' in lesson_results:
            response['lessons']['video'] = lesson_results['video_lesson']
        
        # Add any errors
        errors = {}
        if 'audio_error' in lesson_results:
            errors['audio'] = lesson_results['audio_error']
        if 'video_error' in lesson_results:
            errors['video'] = lesson_results['video_error']
        
        if errors:
            response['errors'] = errors
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate multi-modal lesson: {str(e)}"
        )


@router.get("/audio-lesson/{audio_lesson_id}")
async def get_audio_lesson(
    audio_lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get audio lesson details and playback URL."""
    try:
        audio_lesson = await audio_generation_service.get_audio_lesson(audio_lesson_id)
        if not audio_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio lesson not found"
            )
        
        # Verify user access (check through text lesson)
        text_lesson = await db_service.get_item('MicroLessons', {
            'micro_lesson_id': audio_lesson.get('text_lesson_id')
        })
        
        if text_lesson and text_lesson.get('user_id') != current_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this audio lesson"
            )
        
        return {
            "audio_lesson": audio_lesson,
            "playback_features": [
                "Variable playback speed",
                "Chapter navigation",
                "Key concept timestamps",
                "Transcript available"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audio lesson: {str(e)}"
        )


@router.get("/video-lesson/{video_lesson_id}")
async def get_video_lesson(
    video_lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get video lesson details and playback URL."""
    try:
        video_lesson = await video_generation_service.get_video_lesson(video_lesson_id)
        if not video_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video lesson not found"
            )
        
        # Verify user access
        text_lesson = await db_service.get_item('MicroLessons', {
            'micro_lesson_id': video_lesson.get('text_lesson_id')
        })
        
        if text_lesson and text_lesson.get('user_id') != current_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this video lesson"
            )
        
        return {
            "video_lesson": video_lesson,
            "playback_features": [
                "HD video quality",
                "Interactive elements",
                "Subtitle support",
                "Chapter navigation",
                "Key concept highlights",
                "Accessibility features"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve video lesson: {str(e)}"
        )


@router.get("/user-multimedia-lessons")
async def get_user_multimedia_lessons(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all multimedia lessons for the current user."""
    try:
        user_id = current_user.get('user_id')
        
        # Get audio lessons
        audio_lessons = await audio_generation_service.list_user_audio_lessons(user_id)
        
        # Get video lessons
        video_lessons = await video_generation_service.list_user_video_lessons(user_id)
        
        return {
            "user_id": user_id,
            "multimedia_lessons": {
                "audio": {
                    "count": len(audio_lessons),
                    "lessons": audio_lessons
                },
                "video": {
                    "count": len(video_lessons),
                    "lessons": video_lessons
                }
            },
            "total_multimedia_lessons": len(audio_lessons) + len(video_lessons),
            "available_formats": ["text", "audio", "video"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve multimedia lessons: {str(e)}"
        )


@router.get("/generation-status/{lesson_id}")
async def get_generation_status(
    lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the status of multimedia lesson generation."""
    try:
        # Check text lesson exists and user has access
        text_lesson = await db_service.get_item('MicroLessons', {'micro_lesson_id': lesson_id})
        if not text_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        if text_lesson.get('user_id') != current_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        # Check for audio lesson
        audio_lessons = await audio_generation_service.list_user_audio_lessons(current_user.get('user_id'))
        audio_lesson = next((al for al in audio_lessons if al.get('text_lesson_id') == lesson_id), None)
        
        # Check for video lesson
        video_lessons = await video_generation_service.list_user_video_lessons(current_user.get('user_id'))
        video_lesson = next((vl for vl in video_lessons if vl.get('text_lesson_id') == lesson_id), None)
        
        return {
            "lesson_id": lesson_id,
            "text_lesson": {
                "status": "completed",
                "available": True
            },
            "audio_lesson": {
                "status": "completed" if audio_lesson else "not_generated",
                "available": bool(audio_lesson),
                "audio_lesson_id": audio_lesson.get('audio_lesson_id') if audio_lesson else None
            },
            "video_lesson": {
                "status": "completed" if video_lesson else "not_generated", 
                "available": bool(video_lesson),
                "video_lesson_id": video_lesson.get('video_lesson_id') if video_lesson else None
            },
            "generation_options": {
                "can_generate_audio": not bool(audio_lesson),
                "can_generate_video": not bool(video_lesson),
                "estimated_audio_time": "2-5 minutes",
                "estimated_video_time": "5-15 minutes"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get generation status: {str(e)}"
        )