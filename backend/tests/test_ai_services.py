#!/usr/bin/env python3
"""
Standalone test script for AI services.
Run this to test the AI services without starting the full FastAPI server.
"""

import asyncio
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.iam_helper import iam_helper
from src.services.bedrock import bedrock_service
from src.services.textract import textract_service
from src.services.transcribe import transcribe_service
from src.services.s3 import s3_service


async def test_permissions():
    """Test AWS permissions for all services."""
    print("🔍 Testing AWS Permissions...")
    print("=" * 50)
    
    try:
        # First check basic AWS connectivity
        print("Checking AWS connectivity...")
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
        print(f"✅ Account ID: {identity.get('Account', 'Unknown')}")
        print()
        
        health_check = await iam_helper.get_comprehensive_permissions_check()
        
        print(f"Overall Status: {health_check['overall_status']}")
        print(f"Region: {health_check['region']}")
        print()
        
        for service_name, service_result in health_check['services'].items():
            status = "✅ READY" if service_result.get('has_permissions') else "❌ MISSING PERMISSIONS"
            print(f"{service_name.upper()}: {status}")
            
            if not service_result.get('has_permissions'):
                error_msg = service_result.get('error', 'Unknown error')
                print(f"  Error: {error_msg}")
                
                # More detailed error analysis
                if 'AccessDenied' in error_msg or 'not authorized' in error_msg:
                    print("  Issue: IAM permissions missing")
                elif 'InvalidUserID.NotFound' in error_msg:
                    print("  Issue: AWS credentials not properly configured")
                elif 'region' in error_msg.lower():
                    print("  Issue: Service not available in this region")
                
                if 'required_permissions' in service_result:
                    print("  Required permissions:")
                    for perm in service_result['required_permissions']:
                        print(f"    - {perm}")
            print()
        
        return health_check['overall_status'] == 'ready'
        
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if it's a credentials issue
        if 'credentials' in str(e).lower() or 'Unable to locate credentials' in str(e):
            print("💡 Suggestion: Configure AWS credentials using 'aws configure' or set environment variables")
        elif 'region' in str(e).lower():
            print("💡 Suggestion: Set AWS_REGION environment variable or configure default region")
        
        return False


async def test_bedrock():
    """Test Bedrock Claude integration."""
    print("🤖 Testing Bedrock (Claude 4)...")
    print("=" * 50)
    
    try:
        # First check if Bedrock is available in the region
        import boto3
        from src.config import settings
        
        print(f"Testing Bedrock in region: {settings.aws_region}")
        print(f"Using model: {settings.bedrock_model_id}")
        
        # Test simple prompt
        response = await bedrock_service.invoke_claude(
            prompt="Hello! Please respond with exactly: 'Bedrock test successful'",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ Claude Response: {response}")
        
        # Test content analysis (shorter to avoid token limits)
        sample_content = "Python is a programming language known for its simplicity."
        analysis = await bedrock_service.analyze_content(sample_content, "text")
        
        print(f"✅ Content Analysis: {json.dumps(analysis, indent=2)}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Bedrock test failed: {error_msg}")
        
        # Provide specific guidance based on error type
        if 'AccessDeniedException' in error_msg:
            print("💡 Issue: No permission to access Bedrock")
            print("   Solution: Add bedrock:InvokeModel permission to your IAM user/role")
        elif 'ValidationException' in error_msg and 'model' in error_msg.lower():
            print("💡 Issue: Model not available or incorrect model ID")
            print(f"   Current model: {settings.bedrock_model_id}")
            print("   Solution: Check if Claude 4 is available in your region")
        elif 'ThrottlingException' in error_msg:
            print("💡 Issue: Rate limiting")
            print("   Solution: Wait a moment and try again")
        elif 'region' in error_msg.lower():
            print("💡 Issue: Bedrock not available in this region")
            print("   Solution: Use a region where Bedrock is available (us-east-1, us-west-2, etc.)")
        
        return False


async def test_s3():
    """Test S3 service."""
    print("📁 Testing S3 Service...")
    print("=" * 50)
    
    try:
        # Test bucket info
        bucket_info = await s3_service.get_bucket_info()
        print(f"✅ Bucket Info: {json.dumps(bucket_info, indent=2, default=str)}")
        
        # Test file validation
        validation = await s3_service.validate_file_upload(
            file_size=1024 * 1024,  # 1MB
            content_type="application/pdf",
            file_name="test.pdf"
        )
        print(f"✅ File Validation: {json.dumps(validation, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 test failed: {e}")
        return False


async def test_textract():
    """Test Textract service."""
    print("📄 Testing Textract Service...")
    print("=" * 50)
    
    try:
        # Test supported formats
        formats = await textract_service.get_supported_formats()
        print(f"✅ Supported Formats: {formats}")
        
        # Test document validation
        validation = await textract_service.validate_document(
            file_size=2 * 1024 * 1024,  # 2MB
            content_type="application/pdf"
        )
        print(f"✅ Document Validation: {json.dumps(validation, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Textract test failed: {e}")
        return False


async def test_transcribe():
    """Test Transcribe service."""
    print("🎵 Testing Transcribe Service...")
    print("=" * 50)
    
    try:
        # Test supported formats and languages
        formats = await transcribe_service.get_supported_formats()
        languages = await transcribe_service.get_supported_languages()
        
        print(f"✅ Supported Audio Formats: {formats}")
        print(f"✅ Supported Languages: {[lang['name'] for lang in languages[:5]]}")
        
        # Test audio validation
        validation = await transcribe_service.validate_audio_file(
            file_size=10 * 1024 * 1024,  # 10MB
            content_type="audio/mp3"
        )
        print(f"✅ Audio Validation: {json.dumps(validation, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcribe test failed: {e}")
        return False


async def test_ai_generation():
    """Test AI content generation capabilities."""
    print("🧠 Testing AI Content Generation...")
    print("=" * 50)
    
    try:
        # Test micro-lesson generation (simplified)
        sample_content = "Machine learning is a subset of artificial intelligence."
        
        user_profile = {
            "learning_style": "visual",
            "attention_span": 15,
            "difficulty_level": "intermediate",
            "profession": "software developer"
        }
        
        print("Testing micro-lesson generation...")
        micro_lesson = await bedrock_service.generate_micro_lesson(
            topic_content=sample_content,
            user_profile=user_profile,
            sequence_number=1,
            total_lessons=3
        )
        
        print("✅ Generated Micro-Lesson:")
        print(f"   Title: {micro_lesson.get('title', 'N/A')}")
        print(f"   Duration: {micro_lesson.get('estimated_duration_minutes', 'N/A')} minutes")
        print(f"   Key Concepts: {micro_lesson.get('key_concepts', [])}")
        
        # Test quiz generation (simplified)
        print("Testing quiz generation...")
        quiz = await bedrock_service.generate_quiz(
            lesson_content="Variables in Python store data values.",
            difficulty_level="intermediate",
            num_questions=2
        )
        
        print("✅ Generated Quiz:")
        print(f"   Questions: {quiz.get('total_questions', 0)}")
        print(f"   Total Points: {quiz.get('total_points', 0)}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ AI Generation test failed: {error_msg}")
        
        if 'JSON' in error_msg or 'parse' in error_msg.lower():
            print("💡 Issue: AI response format issue")
            print("   This might be due to model configuration or prompt formatting")
        elif 'token' in error_msg.lower():
            print("💡 Issue: Token limit exceeded")
            print("   Solution: Reduce content length or adjust max_tokens parameter")
        
        return False


async def check_configuration():
    """Check basic configuration."""
    print("⚙️ Configuration Check...")
    print("=" * 30)
    
    from src.config import settings
    import os
    
    print(f"AWS Region: {settings.aws_region}")
    print(f"Bedrock Model: {settings.bedrock_model_id}")
    print(f"Content Bucket: {settings.content_bucket}")
    
    # Check environment variables
    aws_profile = os.getenv('AWS_PROFILE', 'default')
    print(f"AWS Profile: {aws_profile}")
    
    # Check if AWS credentials are configured
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID', 'Not set')
    if aws_access_key != 'Not set':
        print(f"AWS Access Key: {aws_access_key[:8]}...")
    else:
        print("AWS Access Key: Using profile/role credentials")
    
    print()


async def main():
    """Run all tests."""
    print("🚀 SnapStudy AI Services Test Suite")
    print("=" * 50)
    print()
    
    # Check configuration first
    await check_configuration()
    
    tests = [
        ("Permissions Check", test_permissions),
        ("S3 Service", test_s3),
        ("Textract Service", test_textract),
        ("Transcribe Service", test_transcribe),
        ("Bedrock Service", test_bedrock),
        ("AI Generation", test_ai_generation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} FAILED: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI services are ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above and ensure:")
        print("   1. AWS credentials are properly configured")
        print("   2. Required AWS services are enabled in your region")
        print("   3. IAM permissions are correctly set")


if __name__ == "__main__":
    asyncio.run(main())