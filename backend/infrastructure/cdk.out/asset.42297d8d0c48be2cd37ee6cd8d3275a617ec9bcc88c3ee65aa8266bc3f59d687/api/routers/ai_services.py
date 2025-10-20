"""AI Services testing and management endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from ...services.bedrock import bedrock_service
from ...services.textract import textract_service
from ...services.transcribe import transcribe_service
from ...services.s3 import s3_service
from ...services.iam_helper import iam_helper

router = APIRouter()

@router.get("/health-check")
async def ai_services_health_check():
    """Check health and permissions for all AI services."""
    try:
        health_status = await iam_helper.get_comprehensive_permissions_check()
        
        return {
            "status": health_status['overall_status'],
            "region": health_status['region'],
            "services": health_status['services'],
            "timestamp": health_status['timestamp']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@router.post("/test-bedrock")
async def test_bedrock_service(test_prompt: str = "Hello, can you respond with a simple greeting?"):
    """Test Bedrock Claude 4 integration."""
    try:
        response = await bedrock_service.invoke_claude(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        return {
            "status": "success",
            "service": "bedrock",
            "model": "claude-4",
            "test_prompt": test_prompt,
            "response": response,
            "response_length": len(response)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bedrock test failed: {str(e)}"
        )

@router.get("/test-textract")
async def test_textract_service():
    """Test Textract service capabilities."""
    try:
        supported_formats = await textract_service.get_supported_formats()
        
        # Test validation
        validation_result = await textract_service.validate_document(
            file_size=1024 * 1024,  # 1MB
            content_type="application/pdf"
        )
        
        return {
            "status": "success",
            "service": "textract",
            "supported_formats": supported_formats,
            "validation_test": validation_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Textract test failed: {str(e)}"
        )

@router.get("/test-transcribe")
async def test_transcribe_service():
    """Test Transcribe service capabilities."""
    try:
        supported_formats = await transcribe_service.get_supported_formats()
        supported_languages = await transcribe_service.get_supported_languages()
        
        # Test validation
        validation_result = await transcribe_service.validate_audio_file(
            file_size=10 * 1024 * 1024,  # 10MB
            content_type="audio/mp3"
        )
        
        return {
            "status": "success",
            "service": "transcribe",
            "supported_formats": supported_formats,
            "supported_languages": supported_languages[:5],  # First 5 languages
            "validation_test": validation_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcribe test failed: {str(e)}"
        )

@router.get("/test-s3")
async def test_s3_service():
    """Test S3 service capabilities."""
    try:
        bucket_info = await s3_service.get_bucket_info()
        
        # Test validation
        validation_result = await s3_service.validate_file_upload(
            file_size=5 * 1024 * 1024,  # 5MB
            content_type="application/pdf",
            file_name="test.pdf"
        )
        
        return {
            "status": "success",
            "service": "s3",
            "bucket_info": bucket_info,
            "validation_test": validation_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"S3 test failed: {str(e)}"
        )

@router.post("/test-content-analysis")
async def test_content_analysis(content: str = "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."):
    """Test content analysis with Bedrock."""
    try:
        analysis = await bedrock_service.analyze_content(
            content=content,
            content_type="text"
        )
        
        return {
            "status": "success",
            "test": "content_analysis",
            "input_content": content[:100] + "..." if len(content) > 100 else content,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content analysis test failed: {str(e)}"
        )

@router.post("/test-micro-lesson-generation")
async def test_micro_lesson_generation():
    """Test micro-lesson generation with sample data."""
    try:
        sample_content = """
        Python is a high-level programming language known for its simplicity and readability. 
        It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
        Python is widely used in web development, data science, artificial intelligence, and automation.
        """
        
        sample_user_profile = {
            "learning_style": "visual",
            "attention_span": 15,
            "difficulty_level": "intermediate",
            "profession": "software developer"
        }
        
        micro_lesson = await bedrock_service.generate_micro_lesson(
            topic_content=sample_content,
            user_profile=sample_user_profile,
            sequence_number=1,
            total_lessons=3
        )
        
        return {
            "status": "success",
            "test": "micro_lesson_generation",
            "user_profile": sample_user_profile,
            "generated_lesson": micro_lesson
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Micro-lesson generation test failed: {str(e)}"
        )

@router.post("/test-quiz-generation")
async def test_quiz_generation():
    """Test quiz generation with sample lesson content."""
    try:
        sample_lesson = """
        # Introduction to Variables in Python
        
        Variables in Python are used to store data values. Unlike other programming languages, 
        Python has no command for declaring a variable. A variable is created the moment you first assign a value to it.
        
        ## Variable Naming Rules
        - Variable names must start with a letter or underscore
        - Variable names cannot start with a number
        - Variable names can only contain alpha-numeric characters and underscores
        - Variable names are case-sensitive
        """
        
        quiz = await bedrock_service.generate_quiz(
            lesson_content=sample_lesson,
            difficulty_level="intermediate",
            num_questions=3
        )
        
        return {
            "status": "success",
            "test": "quiz_generation",
            "lesson_content": sample_lesson[:100] + "...",
            "generated_quiz": quiz
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation test failed: {str(e)}"
        )

@router.get("/required-permissions")
async def get_required_permissions():
    """Get the required IAM permissions for all AI services."""
    try:
        policy_document = iam_helper.get_required_policy_document()
        
        return {
            "status": "success",
            "policy_document": policy_document,
            "description": "IAM policy document with all required permissions for SnapStudy AI services"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate permissions: {str(e)}"
        )