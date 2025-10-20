"""
Multimedia Processing Lambda Function.

Handles audio and video generation using Amazon Polly and Nova Reel.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.services.audio_generation import audio_generation_service
    from src.services.video_generation import video_generation_service
    from src.services.dynamodb import db_service
    from src.services.s3 import s3_service
    from src.middleware.error_handler import handle_aws_error
except ImportError:
    # Fallback for different path structures
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.services.audio_generation import audio_generation_service
    from src.services.video_generation import video_generation_service
    from src.services.dynamodb import db_service
    from src.services.s3 import s3_service
    from src.middleware.error_handler import handle_aws_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process multimedia generation requests.
    
    Args:
        event: Multimedia generation event
        context: Lambda context
        
    Returns:
        Generation result
    """
    try:
        logger.info(f"Multimedia processor started: {context.aws_request_id}")
        
        # Handle SQS messages
        if 'Records' in event:
            results = []
            for record in event['Records']:
                if 'body' in record:
                    message_body = json.loads(record['body'])
                    result = process_multimedia_task(message_body)
                    results.append(result)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Multimedia processing completed',
                    'results': results,
                    'processed_count': len(results)
                })
            }
        
        # Handle direct invocation
        else:
            result = process_multimedia_task(event)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Multimedia processing completed',
                    'result': result
                })
            }
            
    except Exception as e:
        logger.error(f"Multimedia processing error: {str(e)}", exc_info=True)
        
        # Handle AWS-specific errors
        if hasattr(e, 'response'):
            aws_exception = handle_aws_error(e)
            error_message = str(aws_exception)
        else:
            error_message = str(e)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Multimedia processing failed',
                'message': error_message,
                'request_id': context.aws_request_id
            })
        }

def process_multimedia_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Process a multimedia generation task."""
    try:
        task_type = task.get('task_type')
        lesson_id = task.get('lesson_id')
        
        logger.info(f"Processing multimedia task: {task_type} for lesson: {lesson_id}")
        
        if task_type == 'generate_audio':
            return generate_audio_lesson(task)
        elif task_type == 'generate_video':
            return generate_video_lesson(task)
        elif task_type == 'generate_multimodal':
            return generate_multimodal_lesson(task)
        else:
            raise ValueError(f"Unknown multimedia task type: {task_type}")
            
    except Exception as e:
        logger.error(f"Multimedia task processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def generate_audio_lesson(task: Dict[str, Any]) -> Dict[str, Any]:
    """Generate audio lesson using Amazon Polly."""
    try:
        lesson_id = task.get('lesson_id')
        text_content = task.get('text_content')
        voice_preferences = task.get('voice_preferences', {})
        
        logger.info(f"Generating audio for lesson: {lesson_id}")
        
        # Update status to processing
        db_service.update_item(
            'AudioLessons',
            {'audio_lesson_id': task.get('audio_lesson_id')},
            'SET generation_status = :status',
            {':status': 'processing'}
        )
        
        # Generate audio using Polly
        audio_result = audio_generation_service.generate_audio_lesson(
            text_content=text_content,
            voice_profile=voice_preferences.get('voice_profile', 'professional_female'),
            tone_preference=voice_preferences.get('tone_preference', 'professional'),
            speaking_rate=voice_preferences.get('speaking_rate', 'medium')
        )
        
        # Upload audio to S3
        s3_key = f"audio-lessons/{lesson_id}/{task.get('audio_lesson_id')}.mp3"
        audio_url = s3_service.upload_audio_content(
            audio_result['audio_data'],
            s3_key,
            content_type='audio/mpeg'
        )
        
        # Update audio lesson record
        audio_lesson_data = {
            'audio_url': audio_url,
            'duration_seconds': audio_result.get('duration_seconds', 0),
            'file_size_bytes': audio_result.get('file_size_bytes', 0),
            'voice_profile': audio_result.get('voice_profile', {}),
            'key_timestamps': audio_result.get('key_timestamps', []),
            'transcript': text_content,
            'generation_status': 'completed',
            'generated_at': audio_result.get('generated_at')
        }
        
        db_service.update_item(
            'AudioLessons',
            {'audio_lesson_id': task.get('audio_lesson_id')},
            'SET audio_url = :url, duration_seconds = :duration, file_size_bytes = :size, '
            'voice_profile = :voice, key_timestamps = :timestamps, transcript = :transcript, '
            'generation_status = :status, generated_at = :generated_at',
            {
                ':url': audio_lesson_data['audio_url'],
                ':duration': audio_lesson_data['duration_seconds'],
                ':size': audio_lesson_data['file_size_bytes'],
                ':voice': audio_lesson_data['voice_profile'],
                ':timestamps': audio_lesson_data['key_timestamps'],
                ':transcript': audio_lesson_data['transcript'],
                ':status': 'completed',
                ':generated_at': audio_lesson_data['generated_at']
            }
        )
        
        logger.info(f"Audio generation completed for lesson: {lesson_id}")
        
        return {
            'status': 'success',
            'audio_lesson_id': task.get('audio_lesson_id'),
            'audio_url': audio_url,
            'duration_seconds': audio_result.get('duration_seconds', 0)
        }
        
    except Exception as e:
        logger.error(f"Audio generation error: {str(e)}")
        
        # Update status to failed
        try:
            db_service.update_item(
                'AudioLessons',
                {'audio_lesson_id': task.get('audio_lesson_id')},
                'SET generation_status = :status, error_message = :error',
                {':status': 'failed', ':error': str(e)}
            )
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}

def generate_video_lesson(task: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video lesson using Amazon Nova Reel."""
    try:
        lesson_id = task.get('lesson_id')
        text_content = task.get('text_content')
        video_preferences = task.get('video_preferences', {})
        
        logger.info(f"Generating video for lesson: {lesson_id}")
        
        # Update status to processing
        db_service.update_item(
            'VideoLessons',
            {'video_lesson_id': task.get('video_lesson_id')},
            'SET generation_status = :status',
            {':status': 'processing'}
        )
        
        # Generate video using Nova Reel
        video_result = video_generation_service.generate_video_lesson(
            text_content=text_content,
            visual_style=video_preferences.get('visual_style', 'educational'),
            include_narration=video_preferences.get('include_narration', True),
            include_subtitles=video_preferences.get('include_subtitles', True)
        )
        
        # Upload video to S3
        s3_key = f"video-lessons/{lesson_id}/{task.get('video_lesson_id')}.mp4"
        video_url = s3_service.upload_video_content(
            video_result['video_data'],
            s3_key,
            content_type='video/mp4'
        )
        
        # Update video lesson record
        video_lesson_data = {
            'video_url': video_url,
            'duration_seconds': video_result.get('duration_seconds', 0),
            'file_size_bytes': video_result.get('file_size_bytes', 0),
            'resolution': video_result.get('resolution', '1920x1080'),
            'frame_rate': video_result.get('frame_rate', 30),
            'visual_style': video_result.get('visual_style', {}),
            'interactive_elements': video_result.get('interactive_elements', []),
            'key_timestamps': video_result.get('key_timestamps', []),
            'generation_status': 'completed',
            'generated_at': video_result.get('generated_at')
        }
        
        db_service.update_item(
            'VideoLessons',
            {'video_lesson_id': task.get('video_lesson_id')},
            'SET video_url = :url, duration_seconds = :duration, file_size_bytes = :size, '
            'resolution = :resolution, frame_rate = :frame_rate, visual_style = :style, '
            'interactive_elements = :elements, key_timestamps = :timestamps, '
            'generation_status = :status, generated_at = :generated_at',
            {
                ':url': video_lesson_data['video_url'],
                ':duration': video_lesson_data['duration_seconds'],
                ':size': video_lesson_data['file_size_bytes'],
                ':resolution': video_lesson_data['resolution'],
                ':frame_rate': video_lesson_data['frame_rate'],
                ':style': video_lesson_data['visual_style'],
                ':elements': video_lesson_data['interactive_elements'],
                ':timestamps': video_lesson_data['key_timestamps'],
                ':status': 'completed',
                ':generated_at': video_lesson_data['generated_at']
            }
        )
        
        logger.info(f"Video generation completed for lesson: {lesson_id}")
        
        return {
            'status': 'success',
            'video_lesson_id': task.get('video_lesson_id'),
            'video_url': video_url,
            'duration_seconds': video_result.get('duration_seconds', 0)
        }
        
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        
        # Update status to failed
        try:
            db_service.update_item(
                'VideoLessons',
                {'video_lesson_id': task.get('video_lesson_id')},
                'SET generation_status = :status, error_message = :error',
                {':status': 'failed', ':error': str(e)}
            )
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}

def generate_multimodal_lesson(task: Dict[str, Any]) -> Dict[str, Any]:
    """Generate both audio and video for a lesson."""
    try:
        lesson_id = task.get('lesson_id')
        content_types = task.get('content_types', ['audio', 'video'])
        
        logger.info(f"Generating multimodal content for lesson: {lesson_id}")
        
        results = {}
        
        # Generate audio if requested
        if 'audio' in content_types:
            audio_task = {
                'task_type': 'generate_audio',
                'lesson_id': lesson_id,
                'audio_lesson_id': task.get('audio_lesson_id'),
                'text_content': task.get('text_content'),
                'voice_preferences': task.get('voice_preferences', {})
            }
            results['audio'] = generate_audio_lesson(audio_task)
        
        # Generate video if requested
        if 'video' in content_types:
            video_task = {
                'task_type': 'generate_video',
                'lesson_id': lesson_id,
                'video_lesson_id': task.get('video_lesson_id'),
                'text_content': task.get('text_content'),
                'video_preferences': task.get('video_preferences', {})
            }
            results['video'] = generate_video_lesson(video_task)
        
        # Check if all generations were successful
        all_successful = all(
            result.get('status') == 'success' 
            for result in results.values()
        )
        
        return {
            'status': 'success' if all_successful else 'partial_success',
            'results': results,
            'lesson_id': lesson_id
        }
        
    except Exception as e:
        logger.error(f"Multimodal generation error: {str(e)}")
        return {'status': 'error', 'message': str(e)}