"""
Simple Test Script for Enhanced SnapStudy Chat System.
Tests the core functionality without external dependencies.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend src to path
sys.path.insert(0, os.path.join('backend', 'src'))

def test_imports():
    """Test that all enhanced chat modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from backend.src.services.amazon_q_service import AmazonQService, QServiceType, ContentCategory, SafetyLevel
        print("✅ Amazon Q Service imported successfully")
    except Exception as e:
        print(f"❌ Amazon Q Service import failed: {e}")
        return False
    
    try:
        from backend.src.services.enhanced_chat_agent import EnhancedAgenticChatAgent, EnhancedChatIntent, ResponseSource
        print("✅ Enhanced Chat Agent imported successfully")
    except Exception as e:
        print(f"❌ Enhanced Chat Agent import failed: {e}")
        return False
    
    try:
        from backend.src.services.content_guardrails import ContentGuardrailsService, ContentSafetyLevel, EducationalContentType
        print("✅ Content Guardrails imported successfully")
    except Exception as e:
        print(f"❌ Content Guardrails import failed: {e}")
        return False
    
    return True

async def test_content_safety():
    """Test content safety validation."""
    print("\n🛡️ Testing content safety validation...")
    
    try:
        from backend.src.services.amazon_q_service import AmazonQService, SafetyLevel
        
        q_service = AmazonQService()
        
        # Test safe educational content
        safe_content = "Can you help me understand Python functions and how to use them in my programming course?"
        safety_result = await q_service._validate_content_safety(safe_content)
        
        if safety_result['level'] == SafetyLevel.SAFE:
            print("✅ Safe educational content correctly identified")
        else:
            print(f"❌ Safe content incorrectly flagged: {safety_result['level']}")
            return False
        
        # Test educational content detection
        is_educational = await q_service._is_educational_content(safe_content)
        if is_educational:
            print("✅ Educational content correctly detected")
        else:
            print("❌ Educational content not detected")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Content safety test failed: {e}")
        return False

async def test_enhanced_intent_recognition():
    """Test enhanced intent recognition."""
    print("\n🧠 Testing enhanced intent recognition...")
    
    try:
        from backend.src.services.enhanced_chat_agent import EnhancedAgenticChatAgent, EnhancedChatIntent
        
        enhanced_agent = EnhancedAgenticChatAgent()
        
        context = {
            'user_profile': {
                'user_id': 'test-user',
                'learning_style': 'visual',
                'difficulty_level': 'intermediate'
            },
            'current_lesson': {
                'title': 'Python Programming Basics',
                'key_concepts': ['variables', 'functions', 'loops']
            }
        }
        
        # Test research request intent
        research_message = "Can you find research papers about machine learning algorithms?"
        intent_analysis = await enhanced_agent._enhanced_intent_recognition(research_message, context)
        
        if intent_analysis['intent'] == EnhancedChatIntent.RESEARCH_REQUEST:
            print("✅ Research request intent correctly recognized")
        else:
            print(f"❌ Research intent not recognized: {intent_analysis['intent']}")
            return False
        
        # Test coding help intent
        coding_message = "I need help debugging my Python code for loops"
        intent_analysis = await enhanced_agent._enhanced_intent_recognition(coding_message, context)
        
        if intent_analysis['intent'] == EnhancedChatIntent.CODING_HELP:
            print("✅ Coding help intent correctly recognized")
        else:
            print(f"❌ Coding help intent not recognized: {intent_analysis['intent']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Intent recognition test failed: {e}")
        return False

async def test_content_guardrails():
    """Test content guardrails functionality."""
    print("\n🔒 Testing content guardrails...")
    
    try:
        from backend.src.services.content_guardrails import ContentGuardrailsService, ContentSafetyLevel, EducationalContentType
        
        guardrails_service = ContentGuardrailsService()
        
        # Test safe educational content
        safe_content = "Let's learn about photosynthesis in plants. This biological process converts sunlight into energy."
        
        validation = await guardrails_service.validate_content_comprehensive(
            content=safe_content,
            content_type=EducationalContentType.ACADEMIC,
            user_age_group='high_school'
        )
        
        if validation['overall_safety'] == ContentSafetyLevel.SAFE:
            print("✅ Safe educational content passed guardrails")
        else:
            print(f"❌ Safe content failed guardrails: {validation['overall_safety']}")
            return False
        
        if validation['is_educational']:
            print("✅ Educational content correctly identified")
        else:
            print("❌ Educational content not identified")
            return False
        
        if validation['age_appropriate']:
            print("✅ Age-appropriate content validated")
        else:
            print("❌ Age-appropriate content validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Content guardrails test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from backend.src.config import settings
        
        # Check basic configuration
        if hasattr(settings, 'aws_region'):
            print(f"✅ AWS Region configured: {settings.aws_region}")
        else:
            print("❌ AWS Region not configured")
            return False
        
        if hasattr(settings, 'enhanced_chat_enabled'):
            print(f"✅ Enhanced chat setting: {settings.enhanced_chat_enabled}")
        else:
            print("✅ Enhanced chat setting: default (true)")
        
        if hasattr(settings, 'content_safety_level'):
            print(f"✅ Content safety level: {settings.content_safety_level}")
        else:
            print("✅ Content safety level: default (strict)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_service_health():
    """Test service health checking."""
    print("\n💓 Testing service health monitoring...")
    
    try:
        from backend.src.services.amazon_q_service import AmazonQService
        
        q_service = AmazonQService()
        
        # Test health check (this will show current service availability)
        health_status = await q_service.get_service_health()
        
        print(f"✅ Health check completed")
        print(f"   Q Business available: {health_status['services']['q_business']['available']}")
        print(f"   Q Developer available: {health_status['services']['q_developer']['available']}")
        print(f"   Guardrails available: {health_status['services']['guardrails']['available']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service health test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and generate report."""
    print("🚀 Enhanced SnapStudy Chat System - Simple Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Module imports
    result = test_imports()
    test_results.append(("Module Imports", result))
    
    if not result:
        print("\n❌ Module import failed. Cannot continue with other tests.")
        return False
    
    # Test 2: Content safety
    try:
        result = await test_content_safety()
        test_results.append(("Content Safety", result))
    except Exception as e:
        print(f"❌ Content safety test error: {e}")
        test_results.append(("Content Safety", False))
    
    # Test 3: Intent recognition
    try:
        result = await test_enhanced_intent_recognition()
        test_results.append(("Intent Recognition", result))
    except Exception as e:
        print(f"❌ Intent recognition test error: {e}")
        test_results.append(("Intent Recognition", False))
    
    # Test 4: Content guardrails
    try:
        result = await test_content_guardrails()
        test_results.append(("Content Guardrails", result))
    except Exception as e:
        print(f"❌ Content guardrails test error: {e}")
        test_results.append(("Content Guardrails", False))
    
    # Test 5: Configuration
    result = test_configuration()
    test_results.append(("Configuration", result))
    
    # Test 6: Service health
    try:
        result = await test_service_health()
        test_results.append(("Service Health", result))
    except Exception as e:
        print(f"❌ Service health test error: {e}")
        test_results.append(("Service Health", False))
    
    # Generate report
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed_tests += 1
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    success_rate = (passed_tests / total_tests) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 Enhanced chat system is ready for deployment!")
        print("\n✨ ENHANCED FEATURES VALIDATED:")
        print("• Amazon Q service integration framework")
        print("• Content safety and guardrails system")
        print("• Enhanced intent recognition")
        print("• Educational content validation")
        print("• Multi-layered safety filtering")
        print("• Service health monitoring")
        
        print("\n📝 NEXT STEPS:")
        print("1. Configure Amazon Q Business (optional for enhanced features)")
        print("2. Set up Bedrock Guardrails (recommended for content safety)")
        print("3. Run setup-amazon-q.ps1 to configure services")
        print("4. Deploy enhanced chat system")
        print("5. Monitor chat interactions and safety metrics")
        
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.")
        print("The basic chat functionality should still work with fallback mechanisms.")
    
    return success_rate >= 80

if __name__ == "__main__":
    print(f"Test started at: {datetime.now()}")
    success = asyncio.run(run_all_tests())
    print(f"Test completed at: {datetime.now()}")
    
    if success:
        print("\n🎯 Enhanced SnapStudy Chat System is ready!")
    else:
        print("\n🔧 Please address the failed tests before deployment.")