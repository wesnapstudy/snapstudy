"""
Content Processing Lambda Function.

Handles asynchronous content processing tasks like PDF extraction,
audio transcription, and content analysis.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.services.textract import textract_service
    from src.services.transcribe import transcribe_service
    from src.services.bedrock import bedrock_service
    from src.services.dynamodb import db_service
    from src.services.s3 import s3_service
    from src.middleware.error_handler import handle_aws_error
except ImportError:
    # Fallback for different path structures
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.services.textract import textract_service
    from src.services.transcribe import transcribe_service
    from src.services.bedrock import bedrock_service
    from src.services.dynamodb import db_service
    from src.services.s3 import s3_service
    from src.middleware.error_handler import handle_aws_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process content processing events from S3 or SQS.
    
    Args:
        event: S3 event or SQS message
        context: Lambda context
        
    Returns:
        Processing result
    """
    try:
        logger.info(f"Content processor started: {context.aws_request_id}")
        
        # Handle S3 events
        if 'Records' in event:
            results = []
            for record in event['Records']:
                if 's3' in record:
                    result = process_s3_event(record['s3'])
                    results.append(result)
                elif 'Sns' in record:
                    result = process_sns_message(record['Sns'])
                    results.append(result)
                elif 'body' in record:  # SQS message
                    message_body = json.loads(record['body'])
                    result = process_content_task(message_body)
                    results.append(result)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Content processing completed',
                    'results': results,
                    'processed_count': len(results)
                })
            }
        
        # Handle direct invocation
        else:
            result = process_content_task(event)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Content processing completed',
                    'result': result
                })
            }
            
    except Exception as e:
        logger.error(f"Content processing error: {str(e)}", exc_info=True)
        
        # Handle AWS-specific errors
        if hasattr(e, 'response'):
            aws_exception = handle_aws_error(e)
            error_message = str(aws_exception)
        else:
            error_message = str(e)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Content processing failed',
                'message': error_message,
                'request_id': context.aws_request_id
            })
        }

def process_s3_event(s3_event: Dict[str, Any]) -> Dict[str, Any]:
    """Process S3 upload event."""
    try:
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        logger.info(f"Processing S3 object: s3://{bucket}/{key}")
        
        # Determine content type and process accordingly
        if key.endswith('.pdf'):
            return process_pdf_content(bucket, key)
        elif key.endswith(('.mp3', '.wav', '.m4a')):
            return process_audio_content(bucket, key)
        elif key.endswith(('.mp4', '.mov', '.avi')):
            return process_video_content(bucket, key)
        else:
            logger.warning(f"Unsupported file type: {key}")
            return {'status': 'skipped', 'reason': 'unsupported_file_type'}
            
    except Exception as e:
        logger.error(f"S3 event processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def process_sns_message(sns_message: Dict[str, Any]) -> Dict[str, Any]:
    """Process SNS notification."""
    try:
        message = json.loads(sns_message['Message'])
        logger.info(f"Processing SNS message: {sns_message['Subject']}")
        
        # Handle different SNS message types
        if message.get('source') == 'aws:transcribe':
            return handle_transcribe_completion(message)
        elif message.get('source') == 'aws:textract':
            return handle_textract_completion(message)
        else:
            return process_content_task(message)
            
    except Exception as e:
        logger.error(f"SNS message processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def process_content_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Process a content processing task."""
    try:
        task_type = task.get('task_type')
        lesson_id = task.get('lesson_id')
        
        logger.info(f"Processing task: {task_type} for lesson: {lesson_id}")
        
        if task_type == 'analyze_content':
            return analyze_lesson_content(lesson_id, task.get('content'))
        elif task_type == 'generate_micro_lessons':
            return generate_micro_lessons(lesson_id, task.get('content'))
        elif task_type == 'extract_pdf':
            return extract_pdf_text(task.get('s3_bucket'), task.get('s3_key'))
        elif task_type == 'transcribe_audio':
            return transcribe_audio_file(task.get('s3_bucket'), task.get('s3_key'))
        else:
            raise ValueError(f"Unknown task type: {task_type}")
            
    except Exception as e:
        logger.error(f"Content task processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def process_pdf_content(bucket: str, key: str) -> Dict[str, Any]:
    """Process PDF content using Textract."""
    try:
        # Extract text from PDF
        extracted_text = textract_service.extract_text_from_pdf(f"s3://{bucket}/{key}")
        
        # Get lesson ID from S3 object metadata
        lesson_id = extract_lesson_id_from_key(key)
        
        if lesson_id:
            # Update lesson with extracted content
            db_service.update_lesson(lesson_id, {
                'extracted_content': extracted_text,
                'processing_status': 'text_extracted'
            })
            
            # Trigger content analysis
            analyze_lesson_content(lesson_id, extracted_text)
        
        return {
            'status': 'success',
            'content_length': len(extracted_text),
            'lesson_id': lesson_id
        }
        
    except Exception as e:
        logger.error(f"PDF processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def process_audio_content(bucket: str, key: str) -> Dict[str, Any]:
    """Process audio content using Transcribe."""
    try:
        # Start transcription job
        job_name = f"transcribe-{key.replace('/', '-').replace('.', '-')}"
        transcribe_service.start_transcription_job(
            job_name=job_name,
            media_uri=f"s3://{bucket}/{key}",
            media_format=key.split('.')[-1]
        )
        
        return {
            'status': 'transcription_started',
            'job_name': job_name,
            'media_uri': f"s3://{bucket}/{key}"
        }
        
    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def process_video_content(bucket: str, key: str) -> Dict[str, Any]:
    """Process video content."""
    try:
        # For now, just extract audio and transcribe
        # In the future, could add video analysis
        return process_audio_content(bucket, key)
        
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def analyze_lesson_content(lesson_id: str, content: str) -> Dict[str, Any]:
    """Analyze lesson content using Bedrock."""
    try:
        # Use Bedrock to analyze content
        analysis = bedrock_service.analyze_content(content)
        
        # Update lesson with analysis
        db_service.update_lesson(lesson_id, {
            'content_analysis': analysis,
            'processing_status': 'analyzed'
        })
        
        # Trigger micro-lesson generation
        generate_micro_lessons(lesson_id, content)
        
        return {
            'status': 'success',
            'analysis': analysis,
            'lesson_id': lesson_id
        }
        
    except Exception as e:
        logger.error(f"Content analysis error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def generate_micro_lessons(lesson_id: str, content: str) -> Dict[str, Any]:
    """Generate micro-lessons from content."""
    try:
        # Use Bedrock to generate micro-lessons
        micro_lessons = bedrock_service.generate_micro_lessons(content)
        
        # Save micro-lessons to database
        for i, micro_lesson in enumerate(micro_lessons):
            db_service.create_micro_lesson({
                'lesson_id': lesson_id,
                'sequence_number': i + 1,
                'title': micro_lesson['title'],
                'content': micro_lesson['content'],
                'summary': micro_lesson['summary']
            })
        
        # Update lesson status
        db_service.update_lesson(lesson_id, {
            'processing_status': 'completed',
            'micro_lessons_count': len(micro_lessons)
        })
        
        return {
            'status': 'success',
            'micro_lessons_count': len(micro_lessons),
            'lesson_id': lesson_id
        }
        
    except Exception as e:
        logger.error(f"Micro-lesson generation error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def extract_lesson_id_from_key(s3_key: str) -> str:
    """Extract lesson ID from S3 object key."""
    # Assuming key format: lessons/{lesson_id}/content.pdf
    parts = s3_key.split('/')
    if len(parts) >= 2 and parts[0] == 'lessons':
        return parts[1]
    return None

def handle_transcribe_completion(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Transcribe job completion."""
    try:
        job_name = message.get('jobName')
        status = message.get('jobStatus')
        
        if status == 'COMPLETED':
            # Get transcription result
            result = transcribe_service.get_transcription_result(job_name)
            transcript = result.get('transcript', '')
            
            # Extract lesson ID from job name
            lesson_id = extract_lesson_id_from_job_name(job_name)
            
            if lesson_id:
                # Update lesson with transcript
                db_service.update_lesson(lesson_id, {
                    'transcript': transcript,
                    'processing_status': 'transcribed'
                })
                
                # Trigger content analysis
                analyze_lesson_content(lesson_id, transcript)
            
            return {
                'status': 'success',
                'transcript_length': len(transcript),
                'lesson_id': lesson_id
            }
        else:
            logger.error(f"Transcription job failed: {job_name}")
            return {'status': 'error', 'message': f'Transcription failed: {status}'}
            
    except Exception as e:
        logger.error(f"Transcribe completion handling error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def handle_textract_completion(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Textract job completion."""
    try:
        job_id = message.get('jobId')
        status = message.get('status')
        
        if status == 'SUCCEEDED':
            # Get extraction result
            result = textract_service.get_document_analysis_result(job_id)
            extracted_text = textract_service.extract_text_from_result(result)
            
            # Process the extracted text
            # Implementation depends on how job_id maps to lesson_id
            
            return {
                'status': 'success',
                'extracted_length': len(extracted_text)
            }
        else:
            logger.error(f"Textract job failed: {job_id}")
            return {'status': 'error', 'message': f'Textract failed: {status}'}
            
    except Exception as e:
        logger.error(f"Textract completion handling error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def extract_lesson_id_from_job_name(job_name: str) -> str:
    """Extract lesson ID from transcription job name."""
    # Assuming job name format: transcribe-lessons-{lesson_id}-content-ext
    parts = job_name.split('-')
    if len(parts) >= 3 and parts[0] == 'transcribe' and parts[1] == 'lessons':
        return parts[2]
    return None