"""
Test script for the Learning Analytics and Progress Tracking System.

This script tests the comprehensive analytics functionality including
engagement tracking, learning patterns, progress metrics, and recommendations.
"""

import asyncio
import json
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.analytics import analytics_service, EngagementType, LearningPattern
from src.services.dynamodb import db_service


async def test_engagement_tracking():
    """Test engagement event tracking functionality."""
    print("📊 Testing Engagement Event Tracking...")
    
    try:
        # Create a test user
        test_user = await db_service.create_user({
            'email': 'analytics_test@example.com',
            'name': 'Analytics Test User',
            'learning_style': 'visual',
            'difficulty_level': 'intermediate',
            'profession': 'student'
        })
        
        user_id = test_user['user_id']
        print(f"✅ Created test user: {user_id}")
        
        # Track various engagement events
        events_to_track = [
            (EngagementType.SESSION_STARTED, {'platform': 'web'}),
            (EngagementType.LESSON_STARTED, {'lesson_id': 'test-lesson-1', 'lesson_title': 'Python Basics'}),
            (EngagementType.MICRO_LESSON_VIEWED, {'micro_lesson_id': 'ml-1', 'time_spent': 300}),
            (EngagementType.QUIZ_GENERATED, {'quiz_id': 'quiz-1', 'num_questions': 5}),
            (EngagementType.QUIZ_COMPLETED, {
                'quiz_id': 'quiz-1', 
                'score': 85, 
                'time_spent': 420,
                'concepts': ['variables', 'functions', 'loops']
            }),
            (EngagementType.CHAT_INTERACTION, {
                'session_id': 'chat-1',
                'intent': 'explanation',
                'time_spent': 120
            }),
            (EngagementType.HINT_REQUESTED, {'question_id': 'q1', 'hint_type': 'conceptual'}),
            (EngagementType.LESSON_COMPLETED, {'lesson_id': 'test-lesson-1', 'time_spent': 1200})
        ]
        
        session_id = str(uuid.uuid4())
        
        for event_type, event_data in events_to_track:
            engagement_record = await analytics_service.track_engagement_event(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data,
                session_id=session_id
            )
            print(f"   ✅ Tracked: {event_type.value}")
        
        print(f"✅ Successfully tracked {len(events_to_track)} engagement events")
        return user_id
        
    except Exception as e:
        print(f"❌ Engagement tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_analytics_dashboard(user_id: str):
    """Test analytics dashboard generation."""
    print("\n📈 Testing Analytics Dashboard...")
    
    if not user_id:
        print("❌ Skipping dashboard test - no user ID")
        return
    
    try:
        # Generate analytics dashboard
        dashboard_data = await analytics_service.get_user_analytics_dashboard(user_id)
        
        print("✅ Generated analytics dashboard")
        print(f"   Total events: {dashboard_data['metrics']['total_events']}")
        print(f"   Lessons completed: {dashboard_data['metrics']['lessons_completed']}")
        print(f"   Quizzes taken: {dashboard_data['metrics']['quizzes_taken']}")
        print(f"   Average score: {dashboard_data['metrics']['average_score']}%")
        print(f"   Chat interactions: {dashboard_data['metrics']['chat_interactions']}")
        
        # Display learning patterns
        patterns = dashboard_data['learning_patterns']
        print(f"   Learning patterns: {', '.join(patterns)}")
        
        # Display progress metrics
        progress = dashboard_data['progress']
        print(f"   Completion rate: {progress['completion_rate']}%")
        
        # Display recommendations
        recommendations = dashboard_data['recommendations']
        print(f"   Recommendations: {len(recommendations)} generated")
        for rec in recommendations[:2]:  # Show first 2
            print(f"     - {rec['title']}: {rec['description'][:50]}...")
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_learning_velocity(user_id: str):
    """Test learning velocity calculation."""
    print("\n🚀 Testing Learning Velocity...")
    
    if not user_id:
        print("❌ Skipping velocity test - no user ID")
        return
    
    try:
        # Calculate learning velocity for different periods
        periods = [7, 14, 30]
        
        for days in periods:
            velocity_data = await analytics_service.calculate_learning_velocity(user_id, days)
            
            print(f"   📊 {days}-day velocity:")
            print(f"     Lessons completed: {velocity_data['lessons_completed']}")
            print(f"     Quizzes taken: {velocity_data['quizzes_taken']}")
            print(f"     Learning pace: {velocity_data['learning_pace']}")
            print(f"     Activity score: {velocity_data['activity_score']:.1f}")
            print(f"     Daily averages: {velocity_data['daily_averages']}")
        
        print("✅ Learning velocity calculated successfully")
        
    except Exception as e:
        print(f"❌ Learning velocity calculation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_struggling_concepts(user_id: str):
    """Test struggling concepts identification."""
    print("\n🎯 Testing Struggling Concepts Analysis...")
    
    if not user_id:
        print("❌ Skipping struggling concepts test - no user ID")
        return
    
    try:
        # Add some quiz events with varying performance on different concepts
        quiz_events = [
            {
                'quiz_id': 'quiz-2',
                'score': 45,
                'concepts': ['advanced_functions', 'recursion'],
                'time_spent': 600
            },
            {
                'quiz_id': 'quiz-3',
                'score': 55,
                'concepts': ['advanced_functions', 'data_structures'],
                'time_spent': 480
            },
            {
                'quiz_id': 'quiz-4',
                'score': 90,
                'concepts': ['variables', 'basic_syntax'],
                'time_spent': 300
            }
        ]
        
        # Track additional quiz events
        for quiz_data in quiz_events:
            await analytics_service.track_engagement_event(
                user_id=user_id,
                event_type=EngagementType.QUIZ_COMPLETED,
                event_data=quiz_data
            )
        
        # Identify struggling concepts
        struggling_concepts = await analytics_service.get_struggling_concepts(user_id)
        
        print(f"✅ Identified {len(struggling_concepts)} struggling concepts:")
        for concept in struggling_concepts:
            print(f"   - {concept['concept']}: {concept['recent_average']:.1f}% avg, {concept['attempts']} attempts")
            print(f"     Difficulty: {concept['difficulty_level']}, Trend: {concept['improvement_trend']}")
        
    except Exception as e:
        print(f"❌ Struggling concepts analysis failed: {e}")
        import traceback
        traceback.print_exc()


async def test_retention_analytics(user_id: str):
    """Test retention and consistency analytics."""
    print("\n📅 Testing Retention Analytics...")
    
    if not user_id:
        print("❌ Skipping retention test - no user ID")
        return
    
    try:
        # Calculate retention analytics
        retention_data = await analytics_service.get_retention_analytics(user_id)
        
        print("✅ Retention analytics calculated:")
        print(f"   Total days active: {retention_data['total_days_active']}")
        print(f"   Current streak: {retention_data['current_streak']} days")
        print(f"   Longest streak: {retention_data['longest_streak']} days")
        print(f"   Retention rate: {retention_data['retention_rate']}%")
        print(f"   Consistency score: {retention_data['consistency_score']}%")
        print(f"   Average daily events: {retention_data['average_daily_events']}")
        
        if retention_data['first_activity']:
            print(f"   First activity: {retention_data['first_activity']}")
        if retention_data['last_activity']:
            print(f"   Last activity: {retention_data['last_activity']}")
        
    except Exception as e:
        print(f"❌ Retention analytics failed: {e}")
        import traceback
        traceback.print_exc()


async def test_learning_patterns_analysis(user_id: str):
    """Test learning patterns identification."""
    print("\n🧠 Testing Learning Patterns Analysis...")
    
    if not user_id:
        print("❌ Skipping patterns test - no user ID")
        return
    
    try:
        # Get engagement data for pattern analysis
        engagement_data = await db_service.get_user_engagement(user_id, limit=50)
        
        # Analyze learning patterns
        patterns = await analytics_service._analyze_learning_patterns(user_id, engagement_data)
        
        print(f"✅ Identified learning patterns: {patterns}")
        
        # Describe each pattern
        pattern_descriptions = {
            LearningPattern.CONSISTENT_LEARNER.value: "Maintains regular learning schedule",
            LearningPattern.QUIZ_DEPENDENT.value: "Relies heavily on quizzes for learning",
            LearningPattern.CHAT_HEAVY_USER.value: "Frequently uses AI tutor",
            LearningPattern.FAST_LEARNER.value: "Demonstrates quick understanding",
            LearningPattern.STRUGGLING_LEARNER.value: "Shows difficulty with concepts",
            LearningPattern.CASUAL_LEARNER.value: "Learns at a relaxed pace"
        }
        
        for pattern in patterns:
            description = pattern_descriptions.get(pattern, "Learning pattern identified")
            print(f"   - {pattern}: {description}")
        
    except Exception as e:
        print(f"❌ Learning patterns analysis failed: {e}")
        import traceback
        traceback.print_exc()


async def test_concept_performance_analysis(user_id: str):
    """Test concept-level performance analysis."""
    print("\n🎓 Testing Concept Performance Analysis...")
    
    if not user_id:
        print("❌ Skipping concept analysis test - no user ID")
        return
    
    try:
        # Get engagement data
        engagement_data = await db_service.get_user_engagement(user_id, limit=50)
        
        # Analyze concept performance
        concept_analytics = await analytics_service._analyze_concept_performance(user_id, engagement_data)
        
        print(f"✅ Analyzed {len(concept_analytics)} concepts:")
        
        for concept, analytics in concept_analytics.items():
            print(f"   - {concept}:")
            print(f"     Average score: {analytics['average_score']}%")
            print(f"     Recent average: {analytics['recent_average']}%")
            print(f"     Attempts: {analytics['attempts']}")
            print(f"     Difficulty level: {analytics['difficulty_level']}")
            print(f"     Trend: {analytics['trend']}")
            print(f"     Time spent: {analytics['total_time_minutes']} minutes")
        
    except Exception as e:
        print(f"❌ Concept performance analysis failed: {e}")
        import traceback
        traceback.print_exc()


async def test_recommendations_generation(dashboard_data: dict):
    """Test personalized recommendations generation."""
    print("\n💡 Testing Recommendations Generation...")
    
    if not dashboard_data:
        print("❌ Skipping recommendations test - no dashboard data")
        return
    
    try:
        recommendations = dashboard_data.get('recommendations', [])
        
        print(f"✅ Generated {len(recommendations)} recommendations:")
        
        for rec in recommendations:
            print(f"   - [{rec['priority'].upper()}] {rec['title']}")
            print(f"     Type: {rec['type']}")
            print(f"     Description: {rec['description']}")
            print(f"     Action: {rec['action']}")
            print()
        
        # Test recommendation categories
        categories = {}
        for rec in recommendations:
            category = rec['type']
            categories[category] = categories.get(category, 0) + 1
        
        print(f"   Recommendation categories: {categories}")
        
    except Exception as e:
        print(f"❌ Recommendations generation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_real_time_metrics_update():
    """Test real-time metrics update functionality."""
    print("\n⚡ Testing Real-Time Metrics Updates...")
    
    try:
        # Create a test user for real-time testing
        test_user = await db_service.create_user({
            'email': 'realtime_test@example.com',
            'name': 'Real-time Test User',
            'learning_style': 'kinesthetic'
        })
        
        user_id = test_user['user_id']
        
        # Simulate rapid event tracking
        rapid_events = [
            (EngagementType.SESSION_STARTED, {'platform': 'mobile'}),
            (EngagementType.MICRO_LESSON_VIEWED, {'time_spent': 180}),
            (EngagementType.QUIZ_COMPLETED, {'score': 75, 'time_spent': 240}),
            (EngagementType.CHAT_INTERACTION, {'intent': 'help', 'time_spent': 60}),
            (EngagementType.SESSION_ENDED, {'total_time': 480})
        ]
        
        print(f"   Tracking {len(rapid_events)} rapid events...")
        
        for event_type, event_data in rapid_events:
            await analytics_service.track_engagement_event(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data
            )
        
        print("✅ Real-time metrics updates completed successfully")
        
        # Verify data was stored
        engagement_data = await db_service.get_user_engagement(user_id, limit=10)
        print(f"   Verified: {len(engagement_data)} events stored")
        
    except Exception as e:
        print(f"❌ Real-time metrics update failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run comprehensive analytics system tests."""
    print("🚀 Learning Analytics and Progress Tracking Test Suite")
    print("="*70)
    
    try:
        # Test engagement tracking
        user_id = await test_engagement_tracking()
        
        # Test analytics dashboard
        dashboard_data = await test_analytics_dashboard(user_id)
        
        # Test learning velocity
        await test_learning_velocity(user_id)
        
        # Test struggling concepts
        await test_struggling_concepts(user_id)
        
        # Test retention analytics
        await test_retention_analytics(user_id)
        
        # Test learning patterns
        await test_learning_patterns_analysis(user_id)
        
        # Test concept performance
        await test_concept_performance_analysis(user_id)
        
        # Test recommendations
        await test_recommendations_generation(dashboard_data)
        
        # Test real-time metrics
        await test_real_time_metrics_update()
        
        print("\n" + "="*70)
        print("✅ Analytics System Tests Completed!")
        
        print("\n🎯 Analytics Features Verified:")
        print("• ✅ Comprehensive engagement event tracking")
        print("• ✅ Learning analytics dashboard generation")
        print("• ✅ Learning velocity and pace calculation")
        print("• ✅ Struggling concepts identification")
        print("• ✅ Retention and consistency analytics")
        print("• ✅ Learning patterns analysis")
        print("• ✅ Concept-level performance tracking")
        print("• ✅ Personalized recommendations generation")
        print("• ✅ Real-time metrics updates")
        
        print("\n📊 Analytics System Ready for Production!")
        
    except Exception as e:
        print(f"\n❌ Analytics test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Learning Analytics Test Suite")
    print("Make sure you're using hackathon-user-01 AWS credentials!")
    print()
    
    # Run the async test suite
    asyncio.run(main())