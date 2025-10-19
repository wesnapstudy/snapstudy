"""
Quiz Generation and Evaluation API endpoints.
Provides intelligent quiz creation and assessment capabilities.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
import logging

from ...services.quiz_engine import quiz_engine, QuestionType, DifficultyLevel
from ...services.dynamodb import db_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_adaptive_quiz(
    lesson_id: str,
    user_id: str,
    target_difficulty: Optional[str] = "adaptive",
    num_questions: Optional[int] = None,
    question_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate an adaptive quiz for a specific lesson.
    """
    try:
        # Get lesson content
        lesson = await db_service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Verify lesson belongs to user
        if lesson['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get user profile
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get performance history for adaptive generation
        engagement_history = await db_service.get_user_engagement(user_id, limit=10)
        performance_history = [
            event for event in engagement_history 
            if event.get('event_type') == 'quiz_completed'
        ]
        
        # Generate adaptive quiz
        quiz_data = await quiz_engine.generate_adaptive_quiz(
            lesson_content=lesson.get('description', '') + ' ' + str(lesson.get('learning_objectives', [])),
            user_profile=user,
            performance_history=performance_history,
            target_difficulty=target_difficulty,
            num_questions=num_questions
        )
        
        # Store quiz in database
        quiz_record = await db_service.create_quiz({
            'micro_lesson_id': lesson_id,  # Using lesson_id as micro_lesson_id for now
            'questions': quiz_data['questions'],
            'total_questions': quiz_data['quiz_metadata']['total_questions'],
            'passing_score': quiz_data['quiz_metadata']['passing_score'],
            'difficulty_level': quiz_data['quiz_metadata']['difficulty_level'],
            'estimated_duration_minutes': quiz_data['quiz_metadata']['estimated_duration_minutes'],
            'quiz_metadata': quiz_data['quiz_metadata']
        })
        
        # Track engagement
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'quiz_generated',
            'event_data': {
                'quiz_id': quiz_record['quiz_id'],
                'lesson_id': lesson_id,
                'difficulty': quiz_data['quiz_metadata']['difficulty_level'],
                'num_questions': quiz_data['quiz_metadata']['total_questions'],
                'adaptive_features': quiz_data['quiz_metadata']['adaptive_features']
            }
        })
        
        return {
            "status": "success",
            "message": "Adaptive quiz generated successfully",
            "data": {
                "quiz_id": quiz_record['quiz_id'],
                "quiz_metadata": quiz_data['quiz_metadata'],
                "questions": quiz_data['questions'],
                "instructions": quiz_data['instructions'],
                "hints_available": quiz_data['hints_available']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate adaptive quiz"
        )


@router.post("/submit")
async def submit_quiz(
    quiz_id: str,
    user_id: str,
    answers: Dict[str, str],
    time_spent_seconds: int,
    engagement_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Submit quiz answers for intelligent evaluation.
    """
    try:
        # Get quiz details
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Get user profile for personalized evaluation
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Evaluate quiz submission
        evaluation_results = await quiz_engine.evaluate_quiz_submission(
            quiz_id=quiz_id,
            questions=quiz.get('questions', []),
            user_answers=answers,
            time_spent_seconds=time_spent_seconds,
            user_profile=user
        )
        
        # Track quiz completion
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'quiz_completed',
            'event_data': {
                'quiz_id': quiz_id,
                'score': evaluation_results['overall_score'],
                'time_spent': time_spent_seconds,
                'total_questions': len(quiz.get('questions', [])),
                'engagement_metrics': engagement_metrics or {}
            }
        })
        
        return {
            "status": "success",
            "message": "Quiz evaluated successfully",
            "data": evaluation_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate quiz submission"
        )


@router.post("/hint")
async def get_question_hint(
    quiz_id: str,
    question_id: str,
    user_id: str,
    user_context: Optional[str] = None,
    previous_attempts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get a contextual hint for a specific quiz question.
    """
    try:
        # Get quiz and find the specific question
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Find the specific question
        question = None
        for q in quiz.get('questions', []):
            if q.get('question_id') == question_id:
                question = q
                break
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Get user profile for personalized hints
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate contextual hint
        hint_data = await quiz_engine.generate_contextual_hint(
            question=question,
            user_context={
                'learning_style': user.get('learning_style'),
                'difficulty_level': user.get('difficulty_level'),
                'additional_context': user_context
            },
            previous_attempts=previous_attempts or []
        )
        
        # Track hint request
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'hint_requested',
            'event_data': {
                'quiz_id': quiz_id,
                'question_id': question_id,
                'hint_type': hint_data.get('hint_type'),
                'user_context': user_context
            }
        })
        
        return {
            "status": "success",
            "message": "Hint generated successfully",
            "data": hint_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate hint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate hint"
        )


@router.get("/results/{quiz_id}")
async def get_quiz_results(
    quiz_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Get detailed results for a completed quiz.
    """
    try:
        # Get quiz completion from engagement history
        engagement_history = await db_service.get_user_engagement(user_id, limit=50)
        
        quiz_completion = None
        for event in engagement_history:
            if (event.get('event_type') == 'quiz_completed' and 
                event.get('event_data', {}).get('quiz_id') == quiz_id):
                quiz_completion = event
                break
        
        if not quiz_completion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz results not found"
            )
        
        # Get quiz details
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        event_data = quiz_completion.get('event_data', {})
        
        return {
            "status": "success",
            "message": "Quiz results retrieved successfully",
            "data": {
                "quiz_id": quiz_id,
                "completion_date": quiz_completion.get('timestamp'),
                "score": event_data.get('score', 0),
                "time_spent_seconds": event_data.get('time_spent', 0),
                "total_questions": event_data.get('total_questions', 0),
                "quiz_metadata": quiz.get('quiz_metadata', {}),
                "engagement_metrics": event_data.get('engagement_metrics', {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quiz results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz results"
        )


@router.get("/analytics/{user_id}")
async def get_quiz_analytics(
    user_id: str,
    limit: Optional[int] = 20
) -> Dict[str, Any]:
    """
    Get quiz performance analytics for a user.
    """
    try:
        # Get user's quiz history
        engagement_history = await db_service.get_user_engagement(user_id, limit=limit * 2)
        
        quiz_events = [
            event for event in engagement_history 
            if event.get('event_type') in ['quiz_completed', 'quiz_generated']
        ]
        
        # Analyze performance trends
        completed_quizzes = [
            event for event in quiz_events 
            if event.get('event_type') == 'quiz_completed'
        ]
        
        if not completed_quizzes:
            return {
                "status": "success",
                "message": "No quiz data available",
                "data": {
                    "total_quizzes": 0,
                    "average_score": 0,
                    "performance_trend": "no_data",
                    "strengths": [],
                    "areas_for_improvement": []
                }
            }
        
        # Calculate analytics
        scores = [event.get('event_data', {}).get('score', 0) for event in completed_quizzes]
        times = [event.get('event_data', {}).get('time_spent', 0) for event in completed_quizzes]
        
        analytics = {
            "total_quizzes": len(completed_quizzes),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "average_time_seconds": sum(times) / len(times) if times else 0,
            "performance_trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable",
            "recent_scores": scores[-5:],  # Last 5 scores
            "quiz_frequency": len(completed_quizzes) / max(1, len(set(
                event.get('timestamp', '')[:10] for event in completed_quizzes
            ))),  # Quizzes per day
            "strengths": ["consistent_performance"] if all(s >= 70 for s in scores[-3:]) else [],
            "areas_for_improvement": ["time_management"] if any(t > 600 for t in times[-3:]) else []
        }
        
        return {
            "status": "success",
            "message": "Quiz analytics retrieved successfully",
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Failed to get quiz analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz analytics"
        )


@router.post("/regenerate")
async def regenerate_quiz_question(
    quiz_id: str,
    question_id: str,
    user_id: str,
    difficulty_adjustment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Regenerate a specific quiz question with adjusted difficulty.
    """
    try:
        # Get quiz details
        quiz = await db_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Find the question to regenerate
        question_index = None
        original_question = None
        
        for i, q in enumerate(quiz.get('questions', [])):
            if q.get('question_id') == question_id:
                question_index = i
                original_question = q
                break
        
        if original_question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Get user profile
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Determine new difficulty
        current_difficulty = original_question.get('difficulty', 'medium')
        if difficulty_adjustment == 'easier':
            new_difficulty = 'easy' if current_difficulty != 'easy' else 'easy'
        elif difficulty_adjustment == 'harder':
            new_difficulty = 'hard' if current_difficulty != 'hard' else 'hard'
        else:
            new_difficulty = current_difficulty
        
        # Generate new question (simplified - would use quiz_engine in full implementation)
        new_question = {
            **original_question,
            'question_id': f"{question_id}_v2",
            'difficulty': new_difficulty,
            'regenerated': True,
            'original_question_id': question_id
        }
        
        # Update quiz in database
        updated_questions = quiz.get('questions', []).copy()
        updated_questions[question_index] = new_question
        
        await db_service.update_quiz(quiz_id, {
            'questions': updated_questions,
            'updated_at': quiz_engine.db.datetime.now(quiz_engine.db.timezone.utc).isoformat()
        })
        
        # Track regeneration
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'question_regenerated',
            'event_data': {
                'quiz_id': quiz_id,
                'original_question_id': question_id,
                'new_question_id': new_question['question_id'],
                'difficulty_adjustment': difficulty_adjustment,
                'new_difficulty': new_difficulty
            }
        })
        
        return {
            "status": "success",
            "message": "Question regenerated successfully",
            "data": {
                "new_question": new_question,
                "difficulty_adjustment": difficulty_adjustment,
                "original_difficulty": current_difficulty,
                "new_difficulty": new_difficulty
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate question"
        )