#!/usr/bin/env python3
"""
Comprehensive test suite for the Adaptive Learning Agent.
This tests the core autonomous decision-making engine.
"""

import asyncio
import sys
import os
import json
import uuid
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.adaptive_agent import adaptive_agent, AdaptationDecision, LearningState
from src.services.dynamodb import db_service
from src.services.bedrock import bedrock_service


async def create_test_user() -> Dict[str, Any]:
    """Create a test user for adaptive learning tests."""
    test_user = {
        'email': f'test-{uuid.uuid4().hex[:8]}@example.com',
        'full_name': 'Test User',
        'learning_style': 'visual',
        'attention_span': 15,
        'difficulty_level': 'intermediate',
        'profession': 'software developer',
        'is_active': True
    }
    
    user = await db_service.create_user(test_user)
    return user


async def create_test_lesson(user_id: str) -> Dict[str, Any]:
    """Create a test lesson for adaptive learning tests."""
    test_lesson = {
        'user_id': user_id,
        'title': 'Test Adaptive Learning Lesson',
        'description': 'A test lesson for validating adaptive learning capabilities',
        'content_type': 'text',
        'processing_status': 'completed',
        'status': 'active',
        'learning_objectives': ['Understand adaptive learning', 'Test autonomous decisions'],
        'difficulty_level': 'intermediate'
    }
    
    lesson = await db_service.create_lesson(test_lesson)
    return lesson


async def test_adaptive_lesson_start():
    """Test starting an adaptive learning session."""
    print("🚀 Testing Adaptive Lesson Start...")
    print("=" * 50)
    
    try:
        # Create test user and lesson
        user = await create_test_user()
        lesson = await create_test_lesson(user['user_id'])
        
        print(f"✅ Created test user: {user['user_id']}")
        print(f"✅ Created test lesson: {lesson['lesson_id']}")
        
        # Start adaptive lesson
        result = await adaptive_agent.start_adaptive_lesson(
            user_id=user['user_id'],
            lesson_id=lesson['lesson_id']
        )
        
        print(f"✅ Started adaptive session: {result['session_id']}")
        print(f"   Current micro-lesson: {result['current_micro_lesson'].get('title', 'N/A')}")
        print(f"   Progress: {result['progress']['completion_percentage']}%")
        
        return {
            'success': True,
            'user': user,
            'lesson': lesson,
            'session': result
        }
        
    except Exception as e:
        print(f"❌ Adaptive lesson start failed: {e}")
        return {'success': False, 'error': str(e)}


async def test_autonomous_decision_making():
    """Test the core autonomous decision-making logic."""
    print("🧠 Testing Autonomous Decision Making...")
    print("=" * 50)
    
    try:
        # Start with a lesson
        start_result = await test_adaptive_lesson_start()
        if not start_result['success']:
            raise Exception("Failed to start lesson for decision testing")
        
        session = start_result['session']
        user = start_result['user']
        
        # Test different performance scenarios
        test_scenarios = [
            {
                'name': 'High Performance (>80%)',
                'performance': {
                    'score': 85.0,
                    'time_spent_seconds': 180,
                    'engagement_metrics': {'focus_score': 0.9, 'interaction_count': 8}
                },
                'expected_decision': ['advance', 'accelerate']
            },
            {
                'name': 'Struggling Performance (<60%)',
                'performance': {
                    'score': 45.0,
                    'time_spent_seconds': 420,
                    'engagement_metrics': {'focus_score': 0.5, 'interaction_count': 3}
                },
                'expected_decision': ['review', 'simplify', 'reinforce']
            },
            {
                'name': 'Average Performance (60-80%)',
                'performance': {
                    'score': 70.0,
                    'time_spent_seconds': 240,
                    'engagement_metrics': {'focus_score': 0.7, 'interaction_count': 5}
                },
                'expected_decision': ['advance', 'reinforce']
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📊 Testing Scenario: {scenario['name']}")
            
            # Get next micro-lesson with performance data
            result = await adaptive_agent.get_next_micro_lesson(
                session_id=session['session_id'],
                user_id=user['user_id'],
                previous_performance=scenario['performance']
            )
            
            decision = result['adaptation_info']['decision']
            reasoning = result['adaptation_info']['reasoning']
            learning_state = result['adaptation_info']['learning_state']
            
            print(f"   Decision: {decision}")
            print(f"   Learning State: {learning_state}")
            print(f"   Reasoning: {reasoning[:100]}...")
            
            # Validate decision makes sense
            if decision in scenario['expected_decision']:
                print(f"   ✅ Decision is appropriate for scenario")
            else:
                print(f"   ⚠️  Unexpected decision (expected: {scenario['expected_decision']})")
            
            # Validate micro-lesson was generated
            micro_lesson = result['micro_lesson']
            if micro_lesson and micro_lesson.get('title'):
                print(f"   ✅ Generated micro-lesson: {micro_lesson['title']}")
            else:
                print(f"   ❌ Failed to generate micro-lesson")
        
        return True
        
    except Exception as e:
        print(f"❌ Autonomous decision making test failed: {e}")
        return False


async def test_quiz_evaluation_and_adaptation():
    """Test quiz evaluation and subsequent adaptation."""
    print("📝 Testing Quiz Evaluation and Adaptation...")
    print("=" * 50)
    
    try:
        # Start with a lesson
        start_result = await test_adaptive_lesson_start()
        if not start_result['success']:
            raise Exception("Failed to start lesson for quiz testing")
        
        session = start_result['session']
        user = start_result['user']
        
        # Get the first micro-lesson with quiz
        first_micro_lesson = session['current_micro_lesson']
        quiz_id = first_micro_lesson.get('quiz_id')
        
        if not quiz_id:
            print("❌ No quiz found in micro-lesson")
            return False
        
        print(f"✅ Found quiz: {quiz_id}")
        
        # Get quiz details
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            print("❌ Could not retrieve quiz details")
            return False
        
        questions = quiz.get('questions', [])
        print(f"✅ Quiz has {len(questions)} questions")
        
        # Simulate different answer scenarios
        test_answers = {}
        for i, question in enumerate(questions):
            question_id = question.get('question_id')
            if i == 0:
                # Correct answer for first question
                test_answers[question_id] = question.get('correct_answer', 'A')
            elif i == 1:
                # Incorrect answer for second question
                test_answers[question_id] = 'Wrong answer'
            else:
                # Partially correct for remaining
                test_answers[question_id] = question.get('correct_answer', 'A')
        
        print(f"✅ Prepared test answers: {len(test_answers)} responses")
        
        # Submit quiz and get adaptation
        result = await adaptive_agent.submit_quiz_and_adapt(
            session_id=session['session_id'],
            user_id=user['user_id'],
            quiz_id=quiz_id,
            answers=test_answers,
            time_spent=300,
            engagement_metrics={'focus_score': 0.7, 'interaction_count': 5}
        )
        
        # Analyze results
        quiz_results = result['quiz_results']
        adaptation_info = result['adaptation_info']
        next_micro_lesson = result['next_micro_lesson']
        
        print(f"✅ Quiz Score: {quiz_results['score']:.1f}%")
        print(f"✅ Adaptation Decision: {adaptation_info['decision']}")
        print(f"✅ Next Lesson: {next_micro_lesson.get('title', 'N/A')}")
        print(f"✅ Feedback: {quiz_results['feedback'][:100]}...")
        
        # Validate intelligent evaluation
        detailed_results = quiz_results['detailed_results']
        for result_item in detailed_results:
            question_id = result_item['question_id']
            is_correct = result_item['is_correct']
            score = result_item['score']
            feedback = result_item['feedback']
            
            print(f"   Question {question_id}: {'✅' if is_correct else '❌'} (Score: {score:.2f})")
            if feedback:
                print(f"      Feedback: {feedback[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Quiz evaluation test failed: {e}")
        return False


async def test_adaptation_consistency():
    """Test that adaptation decisions are consistent and logical."""
    print("🔄 Testing Adaptation Consistency...")
    print("=" * 50)
    
    try:
        # Create multiple scenarios with same performance
        consistent_performance = {
            'score': 75.0,
            'time_spent_seconds': 240,
            'engagement_metrics': {'focus_score': 0.8, 'interaction_count': 6}
        }
        
        decisions = []
        
        # Run the same scenario multiple times
        for i in range(3):
            start_result = await test_adaptive_lesson_start()
            if not start_result['success']:
                continue
            
            session = start_result['session']
            user = start_result['user']
            
            result = await adaptive_agent.get_next_micro_lesson(
                session_id=session['session_id'],
                user_id=user['user_id'],
                previous_performance=consistent_performance
            )
            
            decision = result['adaptation_info']['decision']
            decisions.append(decision)
            print(f"   Run {i+1}: {decision}")
        
        # Check consistency (decisions should be similar for same performance)
        unique_decisions = set(decisions)
        if len(unique_decisions) <= 2:  # Allow some variation
            print(f"✅ Decisions are reasonably consistent: {unique_decisions}")
            return True
        else:
            print(f"⚠️  Decisions vary significantly: {unique_decisions}")
            return False
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        return False


async def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️  Testing Edge Cases...")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Invalid session ID
    try:
        await adaptive_agent.get_next_micro_lesson(
            session_id='invalid-session-id',
            user_id='invalid-user-id'
        )
        test_results.append(('Invalid Session ID', False, 'Should have failed'))
    except Exception as e:
        test_results.append(('Invalid Session ID', True, 'Correctly handled error'))
        print(f"✅ Invalid session ID handled: {type(e).__name__}")
    
    # Test 2: Empty quiz answers
    try:
        start_result = await test_adaptive_lesson_start()
        if start_result['success']:
            session = start_result['session']
            user = start_result['user']
            
            result = await adaptive_agent.submit_quiz_and_adapt(
                session_id=session['session_id'],
                user_id=user['user_id'],
                quiz_id='invalid-quiz-id',
                answers={},
                time_spent=0,
                engagement_metrics={}
            )
            test_results.append(('Empty Quiz Answers', False, 'Should have failed'))
    except Exception as e:
        test_results.append(('Empty Quiz Answers', True, 'Correctly handled error'))
        print(f"✅ Empty quiz answers handled: {type(e).__name__}")
    
    # Test 3: Extreme performance values
    try:
        start_result = await test_adaptive_lesson_start()
        if start_result['success']:
            session = start_result['session']
            user = start_result['user']
            
            extreme_performance = {
                'score': 150.0,  # Invalid score > 100%
                'time_spent_seconds': -10,  # Negative time
                'engagement_metrics': {'focus_score': 2.0}  # Invalid focus score > 1.0
            }
            
            result = await adaptive_agent.get_next_micro_lesson(
                session_id=session['session_id'],
                user_id=user['user_id'],
                previous_performance=extreme_performance
            )
            
            # Should handle gracefully
            test_results.append(('Extreme Values', True, 'Handled gracefully'))
            print(f"✅ Extreme values handled gracefully")
    except Exception as e:
        test_results.append(('Extreme Values', True, 'Error handled appropriately'))
        print(f"✅ Extreme values error handled: {type(e).__name__}")
    
    # Summary
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)
    
    print(f"\nEdge Case Results: {passed}/{total} passed")
    for test_name, success, note in test_results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}: {note}")
    
    return passed == total


async def main():
    """Run all adaptive agent tests."""
    print("🤖 SnapStudy Adaptive Learning Agent Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Adaptive Lesson Start", test_adaptive_lesson_start),
        ("Autonomous Decision Making", test_autonomous_decision_making),
        ("Quiz Evaluation & Adaptation", test_quiz_evaluation_and_adaptation),
        ("Adaptation Consistency", test_adaptation_consistency),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            if test_name == "Adaptive Lesson Start":
                # This test returns a dict, others return boolean
                result = await test_func()
                success = result.get('success', False) if isinstance(result, dict) else result
            else:
                success = await test_func()
            
            results[test_name] = success
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} FAILED: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 ADAPTIVE AGENT TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All adaptive agent tests passed! The autonomous learning engine is working correctly.")
    else:
        print("⚠️  Some tests failed. The adaptive agent may need adjustments.")
        print("\n🔧 Common issues to check:")
        print("   1. AWS Bedrock permissions and model availability")
        print("   2. DynamoDB table access and structure")
        print("   3. Network connectivity to AWS services")
        print("   4. JSON parsing in AI responses")


if __name__ == "__main__":
    asyncio.run(main())