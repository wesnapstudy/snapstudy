"""
Test script for Bedrock retry logic with exponential backoff.

This script tests the retry functionality to ensure it handles throttling properly.
"""

import asyncio
import sys
import os
import time
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.bedrock import bedrock_service


async def test_retry_logic_with_mock():
    """Test retry logic with mocked throttling errors."""
    print("🧪 Testing Bedrock Retry Logic (Mocked)")
    print("="*50)
    
    # Configure more aggressive retry settings for testing
    bedrock_service.configure_retry_settings(
        max_retries=3,
        base_delay=0.1,  # Faster for testing
        max_delay=2.0,
        backoff_multiplier=2.0
    )
    
    print(f"Retry settings: {bedrock_service.get_retry_stats()}")
    
    # Test 1: Successful retry after throttling
    print("\n📋 Test 1: Throttling then success")
    
    with patch.object(bedrock_service, 'bedrock_client') as mock_client:
        # First two calls fail with throttling, third succeeds
        mock_client.invoke_model.side_effect = [
            ClientError(
                error_response={'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}},
                operation_name='InvokeModel'
            ),
            ClientError(
                error_response={'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}},
                operation_name='InvokeModel'
            ),
            {
                'body': MagicMock(read=lambda: '{"content": [{"text": "Success after retries!"}]}')
            }
        ]
        
        start_time = time.time()
        try:
            result = await bedrock_service.invoke_claude("Test prompt", max_tokens=100)
            end_time = time.time()
            
            print(f"✅ Success: {result}")
            print(f"   Total time: {end_time - start_time:.2f}s")
            print(f"   Retry attempts: {mock_client.invoke_model.call_count}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Test 2: Non-retryable error
    print("\n📋 Test 2: Non-retryable error")
    
    with patch.object(bedrock_service, 'bedrock_client') as mock_client:
        mock_client.invoke_model.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException', 'Message': 'Invalid input'}},
            operation_name='InvokeModel'
        )
        
        try:
            result = await bedrock_service.invoke_claude("Test prompt", max_tokens=100)
            print(f"❌ Should have failed: {result}")
        except Exception as e:
            print(f"✅ Correctly failed immediately: {type(e).__name__}")
            print(f"   Call count: {mock_client.invoke_model.call_count}")
    
    # Test 3: Max retries exceeded
    print("\n📋 Test 3: Max retries exceeded")
    
    with patch.object(bedrock_service, 'bedrock_client') as mock_client:
        # Always fail with throttling
        mock_client.invoke_model.side_effect = ClientError(
            error_response={'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}},
            operation_name='InvokeModel'
        )
        
        start_time = time.time()
        try:
            result = await bedrock_service.invoke_claude("Test prompt", max_tokens=100)
            print(f"❌ Should have failed: {result}")
        except Exception as e:
            end_time = time.time()
            print(f"✅ Correctly failed after max retries: {type(e).__name__}")
            print(f"   Total time: {end_time - start_time:.2f}s")
            print(f"   Total attempts: {mock_client.invoke_model.call_count}")


async def test_real_bedrock_with_retry():
    """Test real Bedrock calls with retry logic."""
    print("\n🌐 Testing Real Bedrock with Retry Logic")
    print("="*50)
    
    # Configure conservative retry settings for real calls
    bedrock_service.configure_retry_settings(
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0,
        backoff_multiplier=2.0
    )
    
    print(f"Retry settings: {bedrock_service.get_retry_stats()}")
    
    # Test with a simple prompt
    test_prompts = [
        "Hello, please respond with just 'Hi there!'",
        "What is 2+2? Answer with just the number.",
        "Name one color. Just the color name."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📤 Test {i}: {prompt}")
        
        start_time = time.time()
        try:
            result = await bedrock_service.invoke_claude(
                prompt=prompt,
                max_tokens=50,
                temperature=0.1
            )
            end_time = time.time()
            
            print(f"✅ Response: {result.strip()}")
            print(f"   Time taken: {end_time - start_time:.2f}s")
            
            # Small delay between requests to be respectful
            await asyncio.sleep(0.5)
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Failed: {e}")
            print(f"   Time taken: {end_time - start_time:.2f}s")


async def test_delay_calculation():
    """Test the exponential backoff delay calculation."""
    print("\n⏱️  Testing Delay Calculation")
    print("="*30)
    
    # Reset to default settings
    bedrock_service.configure_retry_settings(
        max_retries=5,
        base_delay=1.0,
        max_delay=60.0,
        backoff_multiplier=2.0
    )
    
    print("Delay progression (with jitter):")
    for attempt in range(6):
        delay = bedrock_service._calculate_delay(attempt)
        expected_base = min(1.0 * (2.0 ** attempt), 60.0)
        print(f"  Attempt {attempt}: {delay:.2f}s (base: {expected_base:.2f}s)")


async def main():
    """Run all retry logic tests."""
    print("🚀 Bedrock Retry Logic Test Suite")
    print("="*60)
    
    try:
        # Test delay calculation
        await test_delay_calculation()
        
        # Test mocked retry logic
        await test_retry_logic_with_mock()
        
        # Test real Bedrock calls (comment out if you want to avoid API calls)
        print("\n" + "="*60)
        user_input = input("Test real Bedrock calls? This will make API requests. (y/N): ")
        if user_input.lower() in ['y', 'yes']:
            await test_real_bedrock_with_retry()
        else:
            print("Skipping real Bedrock tests.")
        
        print("\n" + "="*60)
        print("✅ Retry Logic Tests Completed!")
        
        print("\n🎯 Key Features Implemented:")
        print("• Exponential backoff with jitter")
        print("• Configurable retry parameters")
        print("• Retryable vs non-retryable error detection")
        print("• Comprehensive logging")
        print("• Async/await compatibility")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())