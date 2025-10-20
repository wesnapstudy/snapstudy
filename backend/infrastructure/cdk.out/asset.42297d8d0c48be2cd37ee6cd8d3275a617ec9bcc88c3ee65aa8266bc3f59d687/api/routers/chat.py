"""Chat API router for natural agentic tutoring system."""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime

from ...services.chat_agent import chat_agent
from ...services.enhanced_chat_agent import enhanced_chat_agent
from ...services.amazon_q_service import amazon_q_service
from ...services.auth import auth_service
from ...services.dynamodb import db_service

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


class ChatMessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    lesson_context: Optional[Dict[str, Any]] = Field(None, description="Current lesson context")
    learning_progress: Optional[Dict[str, Any]] = Field(None, description="Current learning progress")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    session_id: str
    response: str
    response_type: str
    intent: str
    confidence: float
    metadata: Dict[str, Any] = {}


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    session_id: str
    messages: List[Dict[str, Any]]
    updated_at: Optional[str]


class WebSocketConnectionManager:
    """Manage WebSocket connections for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}  # user_id -> connection_id
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id] = connection_id
        logger.info(f"WebSocket connected: {connection_id} for user {user_id}")
    
    def disconnect(self, connection_id: str, user_id: str):
        """Remove WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                # Remove broken connection
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to user by user_id."""
        connection_id = self.user_connections.get(user_id)
        if connection_id:
            await self.send_personal_message(message, connection_id)


# Global connection manager
manager = WebSocketConnectionManager()


async def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """Get current user from JWT token."""
    try:
        payload = await auth_service.verify_token(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user."""
    return await get_current_user_from_token(credentials.credentials)


@router.websocket("/ws/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str, token: str = None):
    """
    WebSocket endpoint for real-time chat with agentic intent recognition.
    
    Usage: ws://localhost:8000/api/v1/chat/ws/{user_id}?token={jwt_token}
    """
    connection_id = f"ws_{user_id}_{datetime.now().timestamp()}"
    
    try:
        # Authenticate user if token provided
        if token:
            try:
                user = await get_current_user_from_token(token)
                if user['user_id'] != user_id:
                    await websocket.close(code=1008, reason="Unauthorized")
                    return
            except HTTPException:
                await websocket.close(code=1008, reason="Invalid token")
                return
        
        # Accept connection
        await manager.connect(websocket, connection_id, user_id)
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "message": "Connected to SnapStudy AI Tutor! I'm here to help with your learning. Just ask me anything naturally.",
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(welcome_message, connection_id)
        
        # Handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                user_message = message_data.get('message', '')
                session_id = message_data.get('session_id')
                context = message_data.get('context', {})
                
                if not user_message.strip():
                    continue
                
                # Process message with enhanced agentic chat agent (with Amazon Q integration)
                try:
                    response = await enhanced_chat_agent.handle_enhanced_message(
                        user_id=user_id,
                        message=user_message,
                        context=context,
                        session_id=session_id
                    )
                except Exception as e:
                    logger.warning(f"Enhanced chat failed, falling back to base agent: {e}")
                    # Fallback to base chat agent
                    response = await chat_agent.handle_message(
                        user_id=user_id,
                        message=user_message,
                        context=context,
                        session_id=session_id
                    )
                    response['metadata'] = response.get('metadata', {})
                    response['metadata']['fallback_to_base'] = True
                
                # Send response back to client
                response_message = {
                    "type": "chat_response",
                    "session_id": response['session_id'],
                    "response": response['response'],
                    "response_type": response['response_type'],
                    "intent": response['intent'],
                    "confidence": response['confidence'],
                    "metadata": response.get('metadata', {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                await manager.send_personal_message(response_message, connection_id)
                
                # Track engagement
                await db_service.track_engagement({
                    'user_id': user_id,
                    'event_type': 'chat_interaction',
                    'event_data': {
                        'session_id': response['session_id'],
                        'intent': response['intent'],
                        'confidence': response['confidence'],
                        'response_type': response['response_type']
                    }
                })
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                error_message = {
                    "type": "error",
                    "message": "Invalid message format. Please send valid JSON.",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(error_message, connection_id)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                error_message = {
                    "type": "error",
                    "message": "Sorry, I encountered an error processing your message. Please try again.",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(error_message, connection_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(connection_id, user_id)


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a chat message (REST fallback for WebSocket).
    
    This endpoint provides a REST alternative to WebSocket for chat functionality.
    """
    try:
        user_id = current_user['user_id']
        
        # Build context
        context = {
            'current_lesson': request.lesson_context or {},
            'learning_progress': request.learning_progress or {}
        }
        
        # Process message with enhanced agentic chat agent (with Amazon Q integration)
        try:
            response = await enhanced_chat_agent.handle_enhanced_message(
                user_id=user_id,
                message=request.message,
                context=context,
                session_id=request.session_id
            )
        except Exception as e:
            logger.warning(f"Enhanced chat failed, falling back to base agent: {e}")
            # Fallback to base chat agent
            response = await chat_agent.handle_message(
                user_id=user_id,
                message=request.message,
                context=context,
                session_id=request.session_id
            )
            response['metadata'] = response.get('metadata', {})
            response['metadata']['fallback_to_base'] = True
        
        # Track engagement
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'chat_interaction',
            'event_data': {
                'session_id': response['session_id'],
                'intent': response['intent'],
                'confidence': response['confidence'],
                'response_type': response['response_type'],
                'via_rest': True
            }
        })
        
        return ChatMessageResponse(
            session_id=response['session_id'],
            response=response['response'],
            response_type=response['response_type'],
            intent=response['intent'],
            confidence=response['confidence'],
            metadata=response.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve chat history for a session.
    
    Returns the conversation history for the specified session ID.
    Only returns history if the session belongs to the current user.
    """
    try:
        user_id = current_user['user_id']
        
        # Get chat history
        history = await chat_agent.get_chat_history(session_id, user_id)
        
        return ChatHistoryResponse(
            session_id=history['session_id'],
            messages=history['messages'],
            updated_at=history.get('updated_at')
        )
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")


@router.get("/sessions")
async def get_user_chat_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 10
):
    """
    Get recent chat sessions for the current user.
    
    Returns a list of recent chat sessions with basic metadata.
    """
    try:
        user_id = current_user['user_id']
        
        # Get user's chat sessions
        sessions = await db_service.get_user_chat_sessions(user_id, limit)
        
        return {
            'sessions': sessions,
            'total': len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat sessions: {str(e)}")


@router.post("/test-intent")
async def test_intent_recognition(
    request: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Test endpoint for intent recognition (development/debugging).
    
    This endpoint allows testing the intent recognition system without
    generating a full response.
    """
    try:
        user_id = current_user['user_id']
        
        # Build minimal context for testing
        context = {
            'user_message': request.message,
            'user_profile': current_user,
            'current_lesson': request.lesson_context or {},
            'learning_progress': request.learning_progress or {},
            'conversation_history': [],
            'recent_engagement': [],
            'agent_memory': {},
            'context_summary': {}
        }
        
        # Use AgentCore to analyze intent
        intent_analysis = await chat_agent.agent_core.reason_over_context(
            context=context,
            goal="understand_user_intent_and_provide_appropriate_response"
        )
        
        return {
            'message': request.message,
            'intent_analysis': intent_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing intent recognition: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test intent: {str(e)}")


@router.post("/research")
async def get_research_resources(
    request: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get educational research resources using Amazon Q Business.
    
    Specialized endpoint for research assistance and academic resources.
    """
    try:
        user_id = current_user['user_id']
        
        # Extract research topic from message
        topic = request.message.strip()
        if not topic:
            raise HTTPException(status_code=400, detail="Research topic is required")
        
        # Get research resources using Amazon Q
        resources_response = await amazon_q_service.get_educational_resources(
            user_id=user_id,
            topic=topic,
            resource_type="research",
            difficulty_level=current_user.get('difficulty_level', 'intermediate')
        )
        
        if not resources_response['success']:
            raise HTTPException(status_code=500, detail=resources_response.get('reason', 'Failed to get resources'))
        
        # Track engagement
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'research_request',
            'event_data': {
                'topic': topic,
                'resources_found': resources_response['total_found'],
                'service_used': 'amazon_q_business'
            }
        })
        
        return {
            'topic': topic,
            'resources': resources_response['resources'],
            'total_found': resources_response['total_found'],
            'conversation_id': resources_response.get('conversation_id'),
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research resources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get research resources: {str(e)}")


@router.post("/coding-help")
async def get_coding_assistance(
    request: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    programming_language: str = "python"
):
    """
    Get coding assistance using Amazon Q Developer or Q Business.
    
    Specialized endpoint for programming help and code examples.
    """
    try:
        user_id = current_user['user_id']
        
        # Get coding assistance
        coding_response = await amazon_q_service.get_coding_assistance(
            user_id=user_id,
            code_question=request.message,
            programming_language=programming_language,
            context={
                'skill_level': current_user.get('difficulty_level', 'intermediate'),
                'learning_context': request.lesson_context.get('title', 'Programming') if request.lesson_context else 'Programming'
            }
        )
        
        if not coding_response['success']:
            raise HTTPException(status_code=500, detail=coding_response.get('reason', 'Failed to get coding help'))
        
        # Track engagement
        await db_service.track_engagement({
            'user_id': user_id,
            'event_type': 'coding_assistance',
            'event_data': {
                'programming_language': programming_language,
                'question_length': len(request.message),
                'service_used': coding_response.get('service_used', 'amazon_q')
            }
        })
        
        return {
            'response': coding_response['response'],
            'code_examples': coding_response.get('code_examples', []),
            'explanations': coding_response.get('explanations', []),
            'programming_language': programming_language,
            'service_used': coding_response.get('service_used'),
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting coding assistance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get coding assistance: {str(e)}")


@router.get("/q-services/health")
async def check_q_services_health(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check health and availability of Amazon Q services.
    
    Returns status of Q Business, Q Developer, and Guardrails.
    """
    try:
        health_status = await amazon_q_service.get_service_health()
        
        return {
            'overall_health': health_status['overall_health'],
            'services': health_status['services'],
            'enhanced_features_available': health_status['overall_health'],
            'timestamp': health_status['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error checking Q services health: {e}")
        return {
            'overall_health': False,
            'services': {
                'q_business': {'available': False, 'configured': False},
                'q_developer': {'available': False, 'configured': False},
                'guardrails': {'available': False, 'configured': False}
            },
            'enhanced_features_available': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@router.get("/health")
async def chat_health_check():
    """Health check endpoint for chat service."""
    try:
        # Check enhanced chat agent availability
        q_health = await amazon_q_service.get_service_health()
        
        return {
            'status': 'healthy',
            'service': 'enhanced_chat_agent',
            'active_connections': len(manager.active_connections),
            'enhanced_features': {
                'amazon_q_business': q_health['services']['q_business']['available'],
                'amazon_q_developer': q_health['services']['q_developer']['available'],
                'content_guardrails': q_health['services']['guardrails']['available']
            },
            'fallback_available': True,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Enhanced health check failed: {e}")
        return {
            'status': 'healthy',
            'service': 'chat_agent_fallback',
            'active_connections': len(manager.active_connections),
            'enhanced_features': {
                'amazon_q_business': False,
                'amazon_q_developer': False,
                'content_guardrails': False
            },
            'fallback_available': True,
            'timestamp': datetime.now().isoformat()
        }