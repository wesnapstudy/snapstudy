"""
Analytics API router for learning analytics and progress tracking.

Provides comprehensive analytics endpoints for user engagement, performance metrics,
learning patterns, and progress tracking data.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ...services.analytics import analytics_service, EngagementType
from ...services.auth import auth_service
from ...services.dynamodb import db_service

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


class EngagementEventRequest(BaseModel):
    """Request model for tracking engagement events."""
    event_type: str = Field(..., description="Type of engagement event")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    session_id: Optional[str] = Field(None, description="Session identifier")


class AnalyticsDashboardResponse(BaseModel):
    """Response model for analytics dashboard data."""
    user_id: str
    generated_at: str
    metrics: Dict[str, Any]
    learning_patterns: List[str]
    progress: Dict[str, Any]
    concept_analytics: Dict[str, Any]
    retention: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


class LearningVelocityResponse(BaseModel):
    """Response model for learning velocity metrics."""
    period_days: int
    lessons_completed: int
    quizzes_taken: int
    chat_interactions: int
    total_time_spent_minutes: float
    daily_averages: Dict[str, float]
    learning_pace: str
    activity_score: float


class ConceptAnalyticsResponse(BaseModel):
    """Response model for concept-level analytics."""
    concept: str
    average_score: float
    recent_average: float
    attempts: int
    total_time_minutes: float
    difficulty_level: str
    trend: str


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        payload = await auth_service.verify_token(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/events")
async def track_engagement_event(
    request: EngagementEventRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Track a user engagement event for analytics.
    
    This endpoint allows tracking various types of user interactions
    for comprehensive learning analytics.
    """
    try:
        user_id = current_user['user_id']
        
        # Validate event type
        try:
            event_type = EngagementType(request.event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {request.event_type}"
            )
        
        # Track the engagement event
        engagement_record = await analytics_service.track_engagement_event(
            user_id=user_id,
            event_type=event_type,
            event_data=request.event_data,
            session_id=request.session_id
        )
        
        return {
            "status": "success",
            "message": "Engagement event tracked successfully",
            "data": {
                "engagement_id": engagement_record.get('engagement_id'),
                "event_type": request.event_type,
                "timestamp": engagement_record.get('timestamp')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track engagement event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track engagement event"
        )


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive analytics dashboard data for the current user.
    
    Returns metrics, learning patterns, progress tracking, concept analytics,
    retention data, and personalized recommendations.
    """
    try:
        user_id = current_user['user_id']
        
        # Get comprehensive analytics dashboard
        dashboard_data = await analytics_service.get_user_analytics_dashboard(user_id)
        
        return AnalyticsDashboardResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Failed to get analytics dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard"
        )


@router.get("/velocity", response_model=LearningVelocityResponse)
async def get_learning_velocity(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get learning velocity and pace metrics for a specified period.
    
    Analyzes learning activity over the specified number of days
    to calculate velocity, pace, and activity scores.
    """
    try:
        user_id = current_user['user_id']
        
        # Calculate learning velocity
        velocity_data = await analytics_service.calculate_learning_velocity(user_id, days)
        
        if not velocity_data:
            # Return empty metrics if no data
            velocity_data = {
                'period_days': days,
                'lessons_completed': 0,
                'quizzes_taken': 0,
                'chat_interactions': 0,
                'total_time_spent_minutes': 0.0,
                'daily_averages': {'lessons': 0.0, 'quizzes': 0.0, 'time_minutes': 0.0},
                'learning_pace': 'inactive',
                'activity_score': 0.0
            }
        
        return LearningVelocityResponse(**velocity_data)
        
    except Exception as e:
        logger.error(f"Failed to get learning velocity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate learning velocity"
        )


@router.get("/struggling-concepts")
async def get_struggling_concepts(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get concepts where the user is struggling based on performance data.
    
    Identifies concepts with low performance scores and provides
    recommendations for improvement.
    """
    try:
        user_id = current_user['user_id']
        
        # Get struggling concepts
        struggling_concepts = await analytics_service.get_struggling_concepts(user_id)
        
        return {
            "status": "success",
            "message": "Struggling concepts retrieved successfully",
            "data": {
                "struggling_concepts": struggling_concepts,
                "total_concepts": len(struggling_concepts),
                "analysis_date": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get struggling concepts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve struggling concepts"
        )


@router.get("/retention")
async def get_retention_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user retention and engagement consistency metrics.
    
    Provides data on learning streaks, retention rates, and
    consistency patterns over time.
    """
    try:
        user_id = current_user['user_id']
        
        # Get retention analytics
        retention_data = await analytics_service.get_retention_analytics(user_id)
        
        return {
            "status": "success",
            "message": "Retention analytics retrieved successfully",
            "data": retention_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get retention analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve retention analytics"
        )


@router.get("/progress")
async def get_progress_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a summary of learning progress across all activities.
    
    Provides high-level progress metrics including completion rates,
    recent activity, and overall learning trajectory.
    """
    try:
        user_id = current_user['user_id']
        
        # Get recent engagement data for progress calculation
        engagement_data = await db_service.get_user_engagement(user_id, limit=100)
        
        # Calculate progress metrics
        progress_data = await analytics_service._calculate_progress_metrics(user_id, engagement_data)
        
        # Add additional progress context
        progress_summary = {
            **progress_data,
            'last_activity': engagement_data[0].get('timestamp') if engagement_data else None,
            'total_engagement_events': len(engagement_data),
            'progress_trend': 'active' if progress_data.get('recent_activity', {}).get('total_events_this_week', 0) > 0 else 'inactive'
        }
        
        return {
            "status": "success",
            "message": "Progress summary retrieved successfully",
            "data": progress_summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress summary"
        )


@router.get("/patterns")
async def get_learning_patterns(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get identified learning patterns for the user.
    
    Analyzes user behavior to identify learning patterns such as
    consistency, quiz dependency, chat usage, and performance trends.
    """
    try:
        user_id = current_user['user_id']
        
        # Get engagement data for pattern analysis
        engagement_data = await db_service.get_user_engagement(user_id, limit=100)
        
        # Analyze learning patterns
        patterns = await analytics_service._analyze_learning_patterns(user_id, engagement_data)
        
        # Get pattern descriptions
        pattern_descriptions = {
            'consistent_learner': 'Maintains regular learning schedule with steady progress',
            'binge_learner': 'Prefers intensive learning sessions with breaks between',
            'struggling_learner': 'Shows difficulty with concepts and may need additional support',
            'fast_learner': 'Demonstrates quick understanding and high performance',
            'quiz_dependent': 'Relies heavily on quizzes for learning reinforcement',
            'chat_heavy_user': 'Frequently uses AI tutor for help and explanations',
            'perfectionist': 'Strives for high scores and thorough understanding',
            'casual_learner': 'Learns at a relaxed pace with moderate engagement'
        }
        
        pattern_details = [
            {
                'pattern': pattern,
                'description': pattern_descriptions.get(pattern, 'Learning pattern identified'),
                'identified': True
            }
            for pattern in patterns
        ]
        
        return {
            "status": "success",
            "message": "Learning patterns retrieved successfully",
            "data": {
                "patterns": pattern_details,
                "primary_pattern": patterns[0] if patterns else 'casual_learner',
                "analysis_date": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning patterns"
        )


@router.get("/concept-performance")
async def get_concept_performance(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed performance analytics at the concept level.
    
    Provides performance metrics, difficulty levels, and trends
    for individual learning concepts.
    """
    try:
        user_id = current_user['user_id']
        
        # Get engagement data for concept analysis
        engagement_data = await db_service.get_user_engagement(user_id, limit=100)
        
        # Analyze concept performance
        concept_analytics = await analytics_service._analyze_concept_performance(user_id, engagement_data)
        
        # Convert to list format for easier frontend consumption
        concept_list = [
            {
                'concept': concept,
                **analytics
            }
            for concept, analytics in concept_analytics.items()
        ]
        
        # Sort by recent performance (struggling concepts first)
        concept_list.sort(key=lambda x: x.get('recent_average', 0))
        
        return {
            "status": "success",
            "message": "Concept performance retrieved successfully",
            "data": {
                "concepts": concept_list,
                "total_concepts": len(concept_list),
                "struggling_count": len([c for c in concept_list if c.get('difficulty_level') == 'struggling']),
                "mastered_count": len([c for c in concept_list if c.get('difficulty_level') == 'mastered'])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get concept performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve concept performance"
        )


@router.get("/recommendations")
async def get_personalized_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get personalized learning recommendations based on analytics.
    
    Provides actionable recommendations based on learning patterns,
    performance metrics, and engagement data.
    """
    try:
        user_id = current_user['user_id']
        
        # Get analytics data for recommendations
        dashboard_data = await analytics_service.get_user_analytics_dashboard(user_id)
        
        recommendations = dashboard_data.get('recommendations', [])
        
        # Sort recommendations by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
        
        return {
            "status": "success",
            "message": "Recommendations retrieved successfully",
            "data": {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "high_priority_count": len([r for r in recommendations if r.get('priority') == 'high']),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


@router.get("/health")
async def analytics_health_check():
    """Health check endpoint for analytics service."""
    return {
        'status': 'healthy',
        'service': 'analytics',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'engagement_tracking',
            'learning_patterns',
            'progress_metrics',
            'concept_analytics',
            'retention_analysis',
            'personalized_recommendations'
        ]
    }