"""
Adaptive Learning API endpoints.
These endpoints expose the autonomous adaptive learning agent functionality.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
import logging

from ...services.adaptive_agent import adaptive_agent
from ...services.dynamodb import db_service
from ...models.user import UserProfile

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start-lesson")
async def start_adaptive_lesson(
    user_id: str,
    lesson_id: str
) -> Dict[str, Any]:
    """
    Start an adaptive learning session.
    This initializes the autonomous learning loop for a specific lesson.
    """
    try:
        result = await adaptive_agent.start_adaptive_lesson(user_id, lesson_id)
        
        return {
            "status": "success",
            "message": "Adaptive learning session started",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start adaptive lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start adaptive learning session"
        )


@router.get("/next-micro-lesson/{session_id}")
async def get_next_micro_lesson(
    session_id: str,
    user_id: str,
    previous_quiz_score: Optional[float] = None,
    previous_time_spent: Optional[int] = None,
    engagement_focus_score: Optional[float] = None,
    engagement_interaction_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get the next micro-lesson with autonomous adaptation.
    This is where the core adaptive intelligence makes decisions.
    """
    try:
        # Prepare previous performance data if provided
        previous_performance = None
        if previous_quiz_score is not None:
            previous_performance = {
                'score': previous_quiz_score,
                'time_spent_seconds': previous_time_spent or 300,
                'engagement_metrics': {
                    'focus_score': engagement_focus_score or 0.7,
                    'interaction_count': engagement_interaction_count or 5
                }
            }
        
        result = await adaptive_agent.get_next_micro_lesson(
            session_id, user_id, previous_performance
        )
        
        return {
            "status": "success",
            "message": "Next micro-lesson generated",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get next micro-lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate next micro-lesson"
        )


@router.post("/submit-quiz")
async def submit_quiz_and_adapt(
    session_id: str,
    user_id: str,
    quiz_id: str,
    answers: Dict[str, str],
    time_spent_seconds: int,
    engagement_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Submit quiz answers and get autonomous adaptation response.
    This triggers the core adaptation loop.
    """
    try:
        if engagement_metrics is None:
            engagement_metrics = {
                'focus_score': 0.7,
                'interaction_count': len(answers),
                'time_on_questions': time_spent_seconds
            }
        
        result = await adaptive_agent.submit_quiz_and_adapt(
            session_id=session_id,
            user_id=user_id,
            quiz_id=quiz_id,
            answers=answers,
            time_spent=time_spent_seconds,
            engagement_metrics=engagement_metrics
        )
        
        return {
            "status": "success",
            "message": "Quiz submitted and adaptation completed",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to submit quiz and adapt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process quiz submission"
        )


@router.post("/check-answer")
async def check_individual_answer(
    question_id: str,
    user_answer: str,
    quiz_id: str
) -> Dict[str, Any]:
    """
    Check an individual answer with intelligent evaluation.
    Provides immediate feedback without full quiz submission.
    """
    try:
        # Get the quiz and find the specific question
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Find the specific question
        question = None
        for q in quiz.get('questions', []):
            if q.get('question_id') == question_id:
                question = q
                break
        
        if not question:
            raise ValueError(f"Question {question_id} not found in quiz")
        
        # Use Bedrock for intelligent evaluation
        from ...services.bedrock import bedrock_service
        evaluation = await bedrock_service.evaluate_quiz_answer(question, user_answer)
        
        return {
            "status": "success",
            "message": "Answer evaluated",
            "data": {
                "question_id": question_id,
                "is_correct": evaluation.get('is_correct', False),
                "score": evaluation.get('score', 0.0),
                "feedback": evaluation.get('feedback', ''),
                "suggestions": evaluation.get('suggestions', ''),
                "correct_answer": question.get('correct_answer') if not evaluation.get('is_correct') else None
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate answer"
        )


@router.get("/quiz-feedback/{quiz_id}")
async def get_detailed_quiz_feedback(
    quiz_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Get detailed feedback for a completed quiz.
    """
    try:
        # Get quiz results from engagement history
        engagement_history = await db_service.get_user_engagement(user_id, limit=50)
        
        # Find the quiz completion event
        quiz_event = None
        for event in engagement_history:
            if (event.get('event_type') == 'quiz_completed' and 
                event.get('event_data', {}).get('quiz_id') == quiz_id):
                quiz_event = event
                break
        
        if not quiz_event:
            raise ValueError(f"Quiz completion not found for quiz {quiz_id}")
        
        event_data = quiz_event.get('event_data', {})
        
        # Generate comprehensive feedback
        from ...services.bedrock import bedrock_service
        
        feedback_prompt = f"""
        Generate comprehensive learning feedback for a completed quiz:
        
        Quiz Performance:
        - Score: {event_data.get('score', 0)}%
        - Time Spent: {event_data.get('time_spent', 0)} seconds
        
        Provide:
        1. Overall performance summary
        2. Strengths demonstrated
        3. Areas for improvement
        4. Specific study recommendations
        5. Encouragement and next steps
        
        Make it constructive, encouraging, and actionable.
        """
        
        detailed_feedback = await bedrock_service.invoke_claude(
            prompt=feedback_prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "status": "success",
            "message": "Detailed feedback generated",
            "data": {
                "quiz_id": quiz_id,
                "performance_summary": {
                    "score": event_data.get('score', 0),
                    "time_spent": event_data.get('time_spent', 0),
                    "engagement_level": event_data.get('engagement_metrics', {}).get('focus_score', 0.7)
                },
                "detailed_feedback": detailed_feedback.strip(),
                "recommendations": [
                    "Review concepts where you scored below 70%",
                    "Practice similar questions to reinforce learning",
                    "Take breaks between study sessions for better retention"
                ]
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get quiz feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz feedback"
        )


@router.post("/request-hint")
async def request_contextual_hint(
    question_id: str,
    quiz_id: str,
    user_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Request a contextual hint for a specific question.
    """
    try:
        # Get the quiz and find the specific question
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Find the specific question
        question = None
        for q in quiz.get('questions', []):
            if q.get('question_id') == question_id:
                question = q
                break
        
        if not question:
            raise ValueError(f"Question {question_id} not found in quiz")
        
        # Generate contextual hint
        from ...services.bedrock import bedrock_service
        
        hint_prompt = f"""
        Generate a helpful hint for this quiz question without giving away the answer:
        
        Question: {question.get('question_text', '')}
        Question Type: {question.get('question_type', 'multiple_choice')}
        
        User Context: {user_context or 'No additional context provided'}
        
        Provide a hint that:
        1. Guides thinking without revealing the answer
        2. Helps the learner approach the problem correctly
        3. Encourages critical thinking
        4. Is encouraging and supportive
        
        Keep it concise (1-2 sentences).
        """
        
        hint = await bedrock_service.invoke_claude(
            prompt=hint_prompt,
            max_tokens=150,
            temperature=0.7
        )
        
        return {
            "status": "success",
            "message": "Hint generated",
            "data": {
                "question_id": question_id,
                "hint": hint.strip(),
                "hint_type": "contextual"
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to generate hint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate hint"
        )


@router.get("/session-status/{session_id}")
async def get_session_status(
    session_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Get the current status of an adaptive learning session.
    """
    try:
        # Get recent engagement history for this session
        engagement_history = await db_service.get_user_engagement(user_id, limit=20)
        
        # Filter events for this session
        session_events = [
            event for event in engagement_history 
            if event.get('event_data', {}).get('session_id') == session_id
        ]
        
        if not session_events:
            raise ValueError(f"Session {session_id} not found")
        
        # Analyze session progress
        start_event = None
        latest_adaptation = None
        quiz_completions = []
        
        for event in session_events:
            if event.get('event_type') == 'adaptive_lesson_started':
                start_event = event
            elif event.get('event_type') == 'autonomous_adaptation':
                latest_adaptation = event
            elif event.get('event_type') == 'quiz_completed':
                quiz_completions.append(event)
        
        # Calculate progress
        total_micro_lessons = start_event.get('event_data', {}).get('total_micro_lessons', 1) if start_event else 1
        completed_quizzes = len(quiz_completions)
        progress_percentage = (completed_quizzes / total_micro_lessons) * 100
        
        # Get performance trend
        if quiz_completions:
            scores = [event.get('event_data', {}).get('score', 0) for event in quiz_completions]
            avg_score = sum(scores) / len(scores)
            latest_score = scores[-1] if scores else 0
        else:
            avg_score = 0
            latest_score = 0
        
        return {
            "status": "success",
            "message": "Session status retrieved",
            "data": {
                "session_id": session_id,
                "progress": {
                    "completed_micro_lessons": completed_quizzes,
                    "total_micro_lessons": total_micro_lessons,
                    "completion_percentage": progress_percentage
                },
                "performance": {
                    "average_score": avg_score,
                    "latest_score": latest_score,
                    "total_quizzes_completed": len(quiz_completions)
                },
                "latest_adaptation": {
                    "decision": latest_adaptation.get('event_data', {}).get('decision') if latest_adaptation else None,
                    "reasoning": latest_adaptation.get('event_data', {}).get('reasoning') if latest_adaptation else None
                },
                "session_active": progress_percentage < 100
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session status"
        )


@router.post("/force-adaptation")
async def force_adaptation_decision(
    session_id: str,
    user_id: str,
    adaptation_type: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Force a specific adaptation decision (for testing or manual override).
    """
    try:
        valid_adaptations = ['advance', 'review', 'reinforce', 'simplify', 'accelerate', 'complete']
        
        if adaptation_type not in valid_adaptations:
            raise ValueError(f"Invalid adaptation type. Must be one of: {valid_adaptations}")
        
        # Create a forced adaptation decision
        forced_decision = {
            'decision': adaptation_type,
            'reasoning': reason or f'Manually forced adaptation: {adaptation_type}',
            'confidence': 1.0,
            'learning_state': 'manual_override',
            'next_topic_focus': f'Focus based on {adaptation_type} decision',
            'difficulty_adjustment': 'same',
            'estimated_duration': 15
        }
        
        # Get user context for micro-lesson generation
        context = await adaptive_agent._fetch_comprehensive_context(user_id, session_id)
        
        # Generate micro-lesson based on forced decision
        next_micro_lesson = await adaptive_agent._generate_adaptive_micro_lesson(
            context, forced_decision
        )
        
        # Update session state
        await adaptive_agent._update_session_state(session_id, forced_decision, next_micro_lesson)
        
        # Track the manual override
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'manual_adaptation_override',
            'event_data': {
                'session_id': session_id,
                'forced_decision': adaptation_type,
                'reason': reason,
                'micro_lesson_id': next_micro_lesson.get('micro_lesson_id')
            }
        })
        
        return {
            "status": "success",
            "message": f"Forced adaptation to {adaptation_type}",
            "data": {
                "adaptation_decision": forced_decision,
                "next_micro_lesson": next_micro_lesson,
                "session_id": session_id
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to force adaptation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to force adaptation decision"
        )