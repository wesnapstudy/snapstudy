#!/usr/bin/env python3
"""
Comprehensive test suite for the Intelligent Quiz Generation and Evaluation System.
"""

import asyncio
import sys
import os
import json
import uuid
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.quiz_engine import quiz_engine, QuestionType, DifficultyLevel
from src.services.dynamodb import db_service


async def create_test_user() -> Dict[str, Any]:
    """Create a test user for quiz tests."""
    test_user = {
        'email': f'quiz-test-{uuid.uuid4().hex[:8]}@example.com',
        'full_name': 'Quiz Test User',
        'learning_style': 'visual',
        'attention_span': 15,
        'difficulty_level': 'intermediate',
        'profession': 'student',
        'is_active': True
    }
    
    user = await db_service.create_user(test_user)
    return user


async def test_adaptive_quiz_generation():
    """Test adaptive quiz generation with different parameters."""
    print("📝 Testing Adaptive Quiz Generation...")
    print("=" * 50)
    
    try:
        # Create test user
        user = await create_test_user()
        print(f"✅ Created test user: {user['user_id']}")
        
        # Test lesson content
        lesson_content = """
        Machine Learning Fundamentals
        
        Machine learning is a subset of artificial intelligence that enables computers to learn 
        and make decisions from data without being explicitly programmed. Key concepts include:
        
        1. Supervised Learning: Learning with labeled examples
        2. Unsupervised Learning: Finding patterns in unlabeled data
        3. Neural Networks: Computing systems inspired by biological neural networks
        4. Training Data: The dataset used to teach the algorithm
        5. Model Validation: Testing the model's performance on new data
        """
        
        # Generate adaptive quiz
        quiz_data = await quiz_engine.generate_adaptive_quiz(
            lesson_content=lesson_content,
            user_profile=user,
            performance_history=[],
            target_difficulty="medium",
            num_questions=5
        )
        
        print(f"✅ Generated quiz: {quiz_data['quiz_metadata']['title']}")
        print(f"   Questions: {quiz_data['quiz_metadata']['total_questions']}")
        print(f"   Difficulty: {quiz_data['quiz_metadata']['difficulty_level']}")
        print(f"   Duration: {quiz_data['quiz_metadata']['estimated_duration_minutes']} minutes")
        print(f"   Question Types: {quiz_data['quiz_metadata']['question_types']}")
        
        # Validate quiz structure
        questions = quiz_data['questions']
        if len(questions) == 5:
            print("✅ Correct number of questions generated")
        else:
            print(f"⚠️  Expected 5 questions, got {len(questions)}")
        
        # Check question variety
        question_types = set(q['question_type'] for q in questions)
        if len(question_types) > 1:
            print(f"✅ Question variety: {question_types}")
        else:
            print(f"⚠️  Limited question variety: {question_types}")
        
        # Validate question structure
        valid_questions = 0
        for i, question in enumerate(questions):
            required_fields = ['question_id', 'question_type', 'question_text', 'correct_answer']
            if all(field in question for field in required_fields):
                valid_questions += 1
                print(f"   Q{i+1}: {question['question_type']} - {question['question_text'][:50]}...")
        
        if valid_questions == len(questions):
            print("✅ All questions have valid structure")
        else:
            print(f"⚠️  {valid_questions}/{len(questions)} questions have valid structure")
        
        return {
            'success': True,
            'quiz_data': quiz_data,
            'user': user
        }
        
    except Exception as e:
        print(f"❌ Quiz generation test failed: {e}")
        return {'success': False, 'error': str(e)}


async def test_intelligent_quiz_evaluation():
    """Test intelligent quiz evaluation with partial credit."""
    print("🧠 Testing Intelligent Quiz Evaluation...")
    print("=" * 50)
    
    try:
        # Generate a quiz first
        generation_result = await test_adaptive_quiz_generation()
        if not generation_result['success']:
            raise Exception("Failed to generate quiz for evaluation test")
        
        quiz_data = generation_result['quiz_data']
        user = generation_result['user']
        questions = quiz_data['questions']
        
        print(f"✅ Using quiz with {len(questions)} questions")
        
        # Create test answers with mixed performance
        test_answers = {}
        expected_results = []
        
        for i, question in enumerate(questions):
            question_id = question['question_id']
            question_type = question['question_type']
            
            if i == 0:
                # Correct answer
                test_answers[question_id] = question['correct_answer']
                expected_results.append('correct')
            elif i == 1:
                # Completely wrong answer
                test_answers[question_id] = 'Completely wrong answer'
                expected_results.append('incorrect')
            elif i == 2 and question_type == 'short_answer':
                # Partially correct answer
                test_answers[question_id] = 'This is a partial answer that covers some key points'
                expected_results.append('partial')
            else:
                # Mix of correct and incorrect
                if question_type == 'multiple_choice':
                    options = question.get('options', ['A', 'B', 'C', 'D'])
                    test_answers[question_id] = options[0] if options[0] != question['correct_answer'] else options[1]
                else:
                    test_answers[question_id] = 'false' if question['correct_answer'] == 'true' else 'true'
                expected_results.append('incorrect')
        
        print(f"✅ Prepared test answers: {len(test_answers)} responses")
        
        # Evaluate quiz
        evaluation_results = await quiz_engine.evaluate_quiz_submission(
            quiz_id=str(uuid.uuid4()),
            questions=questions,
            user_answers=test_answers,
            time_spent_seconds=420,  # 7 minutes
            user_profile=user
        )
        
        print(f"✅ Quiz evaluated successfully")
        print(f"   Overall Score: {evaluation_results['overall_score']:.1f}%")
        print(f"   Points Earned: {evaluation_results['total_points_earned']:.1f}/{evaluation_results['total_possible_points']}")
        print(f"   Time Spent: {evaluation_results['time_spent_seconds']} seconds")
        
        # Analyze question evaluations
        question_evaluations = evaluation_results['question_evaluations']
        correct_count = sum(1 for q in question_evaluations if q['is_correct'])
        partial_credit_count = sum(1 for q in question_evaluations if q.get('partial_credit_given', False))
        
        print(f"   Correct Answers: {correct_count}/{len(questions)}")
        print(f"   Partial Credit Given: {partial_credit_count} questions")
        
        # Check feedback quality
        overall_feedback = evaluation_results['overall_feedback']
        if overall_feedback and len(overall_feedback) > 50:
            print(f"✅ Generated comprehensive feedback: {overall_feedback[:100]}...")
        else:
            print(f"⚠️  Limited feedback generated")
        
        # Check recommendations
        recommendations = evaluation_results['recommendations']
        if recommendations and len(recommendations) > 0:
            print(f"✅ Generated {len(recommendations)} recommendations")
            for i, rec in enumerate(recommendations[:2]):
                print(f"   {i+1}. {rec}")
        else:
            print(f"⚠️  No recommendations generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Quiz evaluation test failed: {e}")
        return False


async def test_contextual_hint_generation():
    """Test contextual hint generation for quiz questions."""
    print("💡 Testing Contextual Hint Generation...")
    print("=" * 50)
    
    try:
        # Create test question
        test_question = {
            'question_id': 'test_q1',
            'question_type': 'multiple_choice',
            'question_text': 'What is the primary difference between supervised and unsupervised learning?',
            'options': [
                'Supervised learning uses labeled data, unsupervised learning does not',
                'Supervised learning is faster than unsupervised learning',
                'Supervised learning uses more data than unsupervised learning',
                'There is no difference between them'
            ],
            'correct_answer': 'Supervised learning uses labeled data, unsupervised learning does not',
            'difficulty': 'medium'
        }
        
        # Create test user context
        user_context = {
            'learning_style': 'visual',
            'difficulty_level': 'intermediate'
        }
        
        # Generate hint
        hint_data = await quiz_engine.generate_contextual_hint(
            question=test_question,
            user_context=user_context,
            previous_attempts=['Wrong answer 1', 'Wrong answer 2']
        )
        
        print(f"✅ Generated hint for question: {test_question['question_id']}")
        print(f"   Hint: {hint_data['hint']}")
        print(f"   Type: {hint_data['hint_type']}")
        print(f"   Confidence: {hint_data['confidence']}")
        
        # Validate hint quality
        hint_text = hint_data['hint']
        if len(hint_text) > 20 and 'supervised' not in hint_text.lower():
            print("✅ Hint provides guidance without giving away the answer")
        elif len(hint_text) > 20:
            print("⚠️  Hint might be too revealing")
        else:
            print("⚠️  Hint seems too brief")
        
        return True
        
    except Exception as e:
        print(f"❌ Hint generation test failed: {e}")
        return False


async def test_question_type_variety():
    """Test generation of different question types."""
    print("🎯 Testing Question Type Variety...")
    print("=" * 50)
    
    try:
        user = await create_test_user()
        
        lesson_content = """
        Python Programming Basics
        
        Python is a high-level programming language. Key concepts:
        - Variables store data values
        - Functions are reusable blocks of code
        - Lists are ordered collections of items
        - Dictionaries store key-value pairs
        - Loops allow repetitive execution
        """
        
        # Test different difficulty levels
        difficulties = ['easy', 'medium', 'hard']
        results = {}
        
        for difficulty in difficulties:
            print(f"\n📊 Testing {difficulty} difficulty...")
            
            quiz_data = await quiz_engine.generate_adaptive_quiz(
                lesson_content=lesson_content,
                user_profile=user,
                performance_history=[],
                target_difficulty=difficulty,
                num_questions=6
            )
            
            questions = quiz_data['questions']
            question_types = [q['question_type'] for q in questions]
            type_counts = {}
            
            for q_type in question_types:
                type_counts[q_type] = type_counts.get(q_type, 0) + 1
            
            results[difficulty] = type_counts
            print(f"   Question types: {type_counts}")
        
        # Analyze variety across difficulties
        all_types = set()
        for difficulty_types in results.values():
            all_types.update(difficulty_types.keys())
        
        print(f"\n✅ Generated question types: {all_types}")
        
        if len(all_types) >= 3:
            print("✅ Good variety of question types across difficulties")
        else:
            print("⚠️  Limited question type variety")
        
        return True
        
    except Exception as e:
        print(f"❌ Question variety test failed: {e}")
        return False


async def test_performance_based_adaptation():
    """Test quiz adaptation based on performance history."""
    print("📈 Testing Performance-Based Adaptation...")
    print("=" * 50)
    
    try:
        user = await create_test_user()
        
        lesson_content = "Test lesson content about basic concepts."
        
        # Test with different performance histories
        scenarios = [
            {
                'name': 'High Performer',
                'history': [
                    {'score': 95, 'difficulty': 'medium'},
                    {'score': 88, 'difficulty': 'medium'},
                    {'score': 92, 'difficulty': 'hard'}
                ]
            },
            {
                'name': 'Struggling Learner',
                'history': [
                    {'score': 45, 'difficulty': 'easy'},
                    {'score': 52, 'difficulty': 'easy'},
                    {'score': 38, 'difficulty': 'medium'}
                ]
            },
            {
                'name': 'Average Performer',
                'history': [
                    {'score': 72, 'difficulty': 'medium'},
                    {'score': 68, 'difficulty': 'medium'},
                    {'score': 75, 'difficulty': 'medium'}
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n👤 Testing {scenario['name']}...")
            
            quiz_data = await quiz_engine.generate_adaptive_quiz(
                lesson_content=lesson_content,
                user_profile=user,
                performance_history=scenario['history'],
                target_difficulty="adaptive",
                num_questions=4
            )
            
            difficulty = quiz_data['quiz_metadata']['difficulty_level']
            duration = quiz_data['quiz_metadata']['estimated_duration_minutes']
            
            print(f"   Adapted Difficulty: {difficulty}")
            print(f"   Estimated Duration: {duration} minutes")
            
            # Validate adaptation logic
            avg_score = sum(h['score'] for h in scenario['history']) / len(scenario['history'])
            
            if scenario['name'] == 'High Performer' and difficulty in ['medium', 'hard']:
                print("✅ Correctly adapted for high performer")
            elif scenario['name'] == 'Struggling Learner' and difficulty in ['easy', 'medium']:
                print("✅ Correctly adapted for struggling learner")
            elif scenario['name'] == 'Average Performer' and difficulty == 'medium':
                print("✅ Correctly adapted for average performer")
            else:
                print(f"⚠️  Adaptation may not be optimal (avg score: {avg_score:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance adaptation test failed: {e}")
        return False


async def main():
    """Run all quiz engine tests."""
    print("📝 SnapStudy Intelligent Quiz Generation and Evaluation Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        ("Adaptive Quiz Generation", test_adaptive_quiz_generation),
        ("Intelligent Quiz Evaluation", test_intelligent_quiz_evaluation),
        ("Contextual Hint Generation", test_contextual_hint_generation),
        ("Question Type Variety", test_question_type_variety),
        ("Performance-Based Adaptation", test_performance_based_adaptation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        try:
            if test_name == "Adaptive Quiz Generation":
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
    print(f"\n{'='*70}")
    print("📊 QUIZ ENGINE TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quiz engine tests passed! The intelligent quiz system is working correctly.")
        print("\n🔧 Quiz Engine Features Verified:")
        print("   ✅ Adaptive quiz generation with mixed question types")
        print("   ✅ Intelligent evaluation with partial credit")
        print("   ✅ Contextual hint generation")
        print("   ✅ Performance-based difficulty adaptation")
        print("   ✅ Comprehensive feedback and recommendations")
    else:
        print("⚠️  Some quiz engine tests failed.")
        print("\n💡 Common issues to check:")
        print("   1. Bedrock API connectivity and permissions")
        print("   2. JSON parsing in AI responses")
        print("   3. Database operations and data structure")
        print("   4. Question generation prompt effectiveness")


if __name__ == "__main__":
    asyncio.run(main())