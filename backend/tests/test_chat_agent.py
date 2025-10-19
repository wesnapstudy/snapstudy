"""
Test script for the Agentic Chat Agent functionality.

This script tests the core chat agent features including intent recognition
and response generation without requiring a full server setup.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.chat_agent import chat_agent, ChatIntent


async def test_intent_recognition():
    """Test the intent recognition capabilities."""
    print("🧠 Testing Intent Recognition...")
    
    test_messages = [
        {
            'message': "Can you summarize what we've covered so far?",
            'expected_intent': ChatIntent.SUMMARIZATION
        },
        {
            'message': "I don't understand derivatives, can you explain?",
            'expected_intent': ChatIntent.EXPLANATION
        },
        {
            'message': "Test my knowledge on this topic",
            'expected_intent': ChatIntent.QUIZ_REQUEST
        },
        {
            'message': "How am I doing with my progress?",
            'expected_intent': ChatIntent.PROGRESS_INQUIRY
        },
        {
            'message': "This is really difficult, I'm struggling",
            'expected_intent': ChatIntent.ENCOURAGEMENT
        },
        {
            'message': "Hello, how are you?",
            'expected_intent': ChatIntent.GENERAL_CHAT
        }
    ]
    
    # Mock user context
    mock_context = {
        'current_lesson': {
            'lesson_id': 'test-lesson-1',
            'title': 'Introduction to Calculus',
            'content': 'This lesson covers basic calculus concepts including derivatives and integrals.',
            'key_concepts': ['derivatives', 'integrals', 'limits']
        },
        'learning_progress': {
            'completion_percentage': 45.0,
            'current_index': 2,
            'total_micro_lessons': 5
        }
    }
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: {test_case['message'][:50]}... ---")
        
        try:
            # Test intent recognition through the chat agent
            response = await chat_agent.handle_message(
                user_id='test-user-123',
                message=test_case['message'],
                context=mock_context,
                session_id='test-session-1'
            )
            
            print(f"✅ Intent: {response['intent']}")
            print(f"✅ Confidence: {response['confidence']:.2f}")
            print(f"✅ Response Type: {response['response_type']}")
            print(f"✅ Response: {response['response'][:100]}...")
            
            # Check if intent matches expectation (allowing for some flexibility)
            if response['intent'] == test_case['expected_intent'].value:
                print("🎯 Intent recognition: CORRECT")
            else:
                print(f"⚠️  Intent recognition: Expected {test_case['expected_intent'].value}, got {response['intent']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)


async def test_conversation_flow():
    """Test a natural conversation flow."""
    print("💬 Testing Conversation Flow...")
    
    conversation = [
        "Hi, I'm starting to learn calculus",
        "Can you explain what a derivative is?",
        "That's helpful, can you give me an example?",
        "Test my understanding with a question",
        "How am I doing overall?"
    ]
    
    session_id = 'test-conversation-session'
    user_id = 'test-user-456'
    
    mock_context = {
        'current_lesson': {
            'lesson_id': 'calculus-101',
            'title': 'Calculus Fundamentals',
            'content': 'Learn the basics of calculus including derivatives, integrals, and their applications.',
            'key_concepts': ['derivatives', 'integrals', 'chain rule', 'product rule']
        },
        'learning_progress': {
            'completion_percentage': 25.0,
            'current_index': 1,
            'total_micro_lessons': 4
        }
    }
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Message {i} ---")
        print(f"Student: {message}")
        
        try:
            response = await chat_agent.handle_message(
                user_id=user_id,
                message=message,
                context=mock_context,
                session_id=session_id
            )
            
            print(f"AI Tutor: {response['response']}")
            print(f"[Intent: {response['intent']}, Confidence: {response['confidence']:.2f}]")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)


async def test_context_awareness():
    """Test context awareness across different scenarios."""
    print("🎯 Testing Context Awareness...")
    
    scenarios = [
        {
            'name': 'No Active Lesson',
            'context': {'current_lesson': {}, 'learning_progress': {}},
            'message': 'Can you summarize the lesson?'
        },
        {
            'name': 'High Performance Context',
            'context': {
                'current_lesson': {'title': 'Advanced Topics', 'key_concepts': ['complex analysis']},
                'learning_progress': {'completion_percentage': 90.0},
                'recent_engagement': [
                    {'event_type': 'quiz_completed', 'event_data': {'score': 95.0}},
                    {'event_type': 'quiz_completed', 'event_data': {'score': 88.0}}
                ]
            },
            'message': 'How am I doing?'
        },
        {
            'name': 'Struggling Student Context',
            'context': {
                'current_lesson': {'title': 'Basic Concepts', 'key_concepts': ['fundamentals']},
                'learning_progress': {'completion_percentage': 15.0},
                'recent_engagement': [
                    {'event_type': 'quiz_completed', 'event_data': {'score': 45.0}},
                    {'event_type': 'quiz_completed', 'event_data': {'score': 38.0}}
                ]
            },
            'message': 'This is too hard for me'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Message: {scenario['message']}")
        
        try:
            response = await chat_agent.handle_message(
                user_id='test-context-user',
                message=scenario['message'],
                context=scenario['context'],
                session_id=f"test-{scenario['name'].lower().replace(' ', '-')}"
            )
            
            print(f"Response: {response['response']}")
            print(f"Intent: {response['intent']} (confidence: {response['confidence']:.2f})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)


async def main():
    """Run all tests."""
    print("🚀 Starting Agentic Chat Agent Tests")
    print("="*60)
    
    try:
        await test_intent_recognition()
        await test_conversation_flow()
        await test_context_awareness()
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async test suite
    asyncio.run(main())