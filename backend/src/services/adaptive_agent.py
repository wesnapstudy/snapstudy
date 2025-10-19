"""
Autonomous Adaptive Learning Agent - The Core Intelligence Engine of SnapStudy.

This is the heart of the system that makes autonomous decisions about learning paths,
generates personalized content, and adapts in real-time based on user performance.

Uses Amazon Bedrock AgentCore primitives for true autonomous reasoning and planning.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import uuid
import boto3

from .bedrock import bedrock_service
from .dynamodb import db_service
from ..models.lesson import LessonStatus, ProcessingStatus
from ..config import settings

logger = logging.getLogger(__name__)


class AdaptationDecision(str, Enum):
    """Possible adaptation decisions the agent can make."""
    ADVANCE = "advance"           # Move to next concept
    REVIEW = "review"            # Review current concept with different approach
    REINFORCE = "reinforce"      # Additional practice on current concept
    SIMPLIFY = "simplify"        # Reduce complexity
    ACCELERATE = "accelerate"    # Increase difficulty/pace
    COMPLETE = "complete"        # Lesson is complete


class LearningState(str, Enum):
    """Current learning state of the user."""
    STRUGGLING = "struggling"     # Score < 60%
    LEARNING = "learning"        # Score 60-80%
    MASTERING = "mastering"      # Score > 80%
    ENGAGED = "engaged"          # High engagement metrics
    DISTRACTED = "distracted"    # Low engagement metrics


class BedrockAgentCore:
    """
    Amazon Bedrock AgentCore primitives integration for autonomous reasoning.
    This provides the core agent capabilities: reasoning, planning, memory, and function invocation.
    """
    
    def __init__(self):
        self.bedrock_agent_client = boto3.client('bedrock-agent-runtime', region_name=settings.aws_region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=settings.aws_region)
        
        # Agent configuration
        self.agent_id = settings.bedrock_agent_id if hasattr(settings, 'bedrock_agent_id') else None
        self.agent_alias_id = settings.bedrock_agent_alias_id if hasattr(settings, 'bedrock_agent_alias_id') else 'TSTALIASID'
        
        # Memory store for agent state
        self.memory_store = {}
        
    async def reason_over_context(self, context: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Use Bedrock Agent reasoning capabilities to analyze context and make decisions.
        This is the core autonomous reasoning function.
        """
        try:
            # Prepare reasoning prompt with structured context
            reasoning_prompt = self._create_reasoning_prompt(context, goal)
            
            if self.agent_id:
                # Use Bedrock Agent if configured
                response = await self._invoke_bedrock_agent(reasoning_prompt, context)
            else:
                # Fallback to direct Claude invocation with agent-like reasoning
                response = await self._invoke_claude_reasoning(reasoning_prompt, context)
            
            return response
            
        except Exception as e:
            logging.error(f"AgentCore reasoning failed: {e}")
            return self._fallback_reasoning(context, goal)
    
    async def plan_learning_sequence(self, context: Dict[str, Any], objective: str) -> List[Dict[str, Any]]:
        """
        Use AgentCore planning capabilities to create multi-step learning sequences.
        """
        try:
            planning_prompt = f"""
            Plan a learning sequence to achieve: {objective}
            
            Context: {json.dumps(context, indent=2)}
            
            Create a step-by-step plan with:
            1. Learning objectives for each step
            2. Content difficulty progression
            3. Assessment checkpoints
            4. Adaptation triggers
            
            Return as JSON array of steps.
            """
            
            if self.agent_id:
                response = await self._invoke_bedrock_agent(planning_prompt, context)
            else:
                response = await bedrock_service.invoke_claude(
                    prompt=planning_prompt,
                    max_tokens=1500,
                    temperature=0.3
                )
                
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    response = self._fallback_plan()
            
            return response.get('steps', []) if isinstance(response, dict) else []
            
        except Exception as e:
            logging.error(f"AgentCore planning failed: {e}")
            return self._fallback_plan()
    
    async def update_memory(self, user_id: str, experience: Dict[str, Any]) -> None:
        """
        Update agent memory with learning experiences for future reasoning.
        """
        try:
            memory_key = f"user_{user_id}_learning_memory"
            
            if memory_key not in self.memory_store:
                self.memory_store[memory_key] = {
                    'experiences': [],
                    'patterns': {},
                    'preferences': {},
                    'performance_history': []
                }
            
            # Add new experience
            self.memory_store[memory_key]['experiences'].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'experience': experience
            })
            
            # Keep only recent experiences (last 50)
            if len(self.memory_store[memory_key]['experiences']) > 50:
                self.memory_store[memory_key]['experiences'] = \
                    self.memory_store[memory_key]['experiences'][-50:]
            
            # Update patterns based on experiences
            await self._update_learning_patterns(memory_key)
            
        except Exception as e:
            logging.error(f"Memory update failed: {e}")
    
    async def retrieve_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve agent memory for context-aware decision making.
        """
        memory_key = f"user_{user_id}_learning_memory"
        return self.memory_store.get(memory_key, {
            'experiences': [],
            'patterns': {},
            'preferences': {},
            'performance_history': []
        })
    
    async def invoke_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        """
        AgentCore function invocation for calling specific learning functions.
        """
        try:
            if function_name == "generate_micro_lesson":
                return await bedrock_service.generate_micro_lesson(**parameters)
            elif function_name == "generate_quiz":
                return await bedrock_service.generate_quiz(**parameters)
            elif function_name == "evaluate_answer":
                return await bedrock_service.evaluate_quiz_answer(**parameters)
            elif function_name == "analyze_performance":
                return await self._analyze_performance(**parameters)
            elif function_name == "summarize_lesson":
                return await self._summarize_lesson(**parameters)
            elif function_name == "explain_concept":
                return await self._explain_concept(**parameters)
            elif function_name == "generate_practice_quiz":
                return await self._generate_practice_quiz(**parameters)
            elif function_name == "show_progress":
                return await self._show_progress(**parameters)
            else:
                raise ValueError(f"Unknown function: {function_name}")
                
        except Exception as e:
            logging.error(f"Function invocation failed: {e}")
            raise
    
    async def _invoke_bedrock_agent(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke Bedrock Agent with proper session management.
        """
        try:
            session_id = context.get('session_id', str(uuid.uuid4()))
            
            response = self.bedrock_agent_client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=prompt
            )
            
            # Process agent response
            completion = ""
            for event in response.get('completion', []):
                if 'chunk' in event:
                    completion += event['chunk'].get('bytes', b'').decode('utf-8')
            
            # Parse JSON response
            try:
                return json.loads(completion)
            except json.JSONDecodeError:
                return {'reasoning': completion, 'decision': 'advance'}
                
        except Exception as e:
            logging.error(f"Bedrock Agent invocation failed: {e}")
            raise
    
    async def _invoke_claude_reasoning(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to Claude with agent-like reasoning structure.
        """
        system_prompt = """
        You are an autonomous learning agent with advanced reasoning capabilities.
        You have access to memory, can plan multi-step sequences, and make intelligent decisions.
        Always respond with structured JSON that includes your reasoning process.
        """
        
        response = await bedrock_service.invoke_claude(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3,
            system_prompt=system_prompt
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                'reasoning': response,
                'decision': 'advance',
                'confidence': 0.7
            }
    
    def _create_reasoning_prompt(self, context: Dict[str, Any], goal: str) -> str:
        """
        Create a structured reasoning prompt for the agent.
        """
        if goal == "understand_user_intent_and_provide_appropriate_response":
            return self._create_intent_recognition_prompt(context)
        else:
            return f"""
            AUTONOMOUS LEARNING AGENT REASONING TASK
            
            GOAL: {goal}
            
            CONTEXT:
            {json.dumps(context, indent=2)}
            
            REASONING FRAMEWORK:
            1. Analyze current learner state and performance
            2. Identify knowledge gaps and learning patterns
            3. Consider user preferences and constraints
            4. Evaluate possible adaptation strategies
            5. Select optimal decision with confidence score
            6. Plan next steps and content generation
            
            AVAILABLE DECISIONS:
            - advance: Move to next concept
            - review: Review current concept differently  
            - reinforce: Additional practice on current concept
            - simplify: Reduce complexity
            - accelerate: Increase difficulty/pace
            - complete: Mark lesson as complete
            
            Respond with JSON:
            {{
                "reasoning": "Step-by-step analysis of the situation",
                "decision": "selected_decision",
                "confidence": 0.85,
                "next_actions": ["action1", "action2"],
                "content_focus": "what to focus on next",
                "difficulty_adjustment": "easier|same|harder",
                "estimated_duration": 15
            }}
            """
    
    def _create_intent_recognition_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create a specialized prompt for natural language intent recognition.
        """
        user_message = context.get('user_message', '')
        conversation_history = context.get('conversation_history', [])
        current_lesson = context.get('current_lesson', {})
        user_profile = context.get('user_profile', {})
        context_summary = context.get('context_summary', {})
        
        # Build conversation context
        recent_messages = conversation_history[-3:] if conversation_history else []
        conversation_context = ""
        if recent_messages:
            conversation_context = "Recent conversation:\n"
            for msg in recent_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]
                conversation_context += f"{role}: {content}\n"
        
        return f"""
        NATURAL LANGUAGE INTENT RECOGNITION TASK
        
        You are an AI tutor analyzing a student's message to understand their intent and provide the most helpful response.
        
        STUDENT MESSAGE: "{user_message}"
        
        CONTEXT:
        - Current lesson: {current_lesson.get('title', 'No active lesson')}
        - Has active lesson: {context_summary.get('has_active_lesson', False)}
        - Student's learning style: {user_profile.get('learning_style', 'unknown')}
        - Recent quiz performance: {context_summary.get('recent_quiz_performance', 'No recent quizzes')}
        - Conversation length: {context_summary.get('conversation_length', 0)} messages
        
        {conversation_context}
        
        INTENT CATEGORIES:
        1. "summarization" - Student wants a summary of current lesson/content
           Examples: "Can you summarize?", "What have we covered?", "Give me the main points"
        
        2. "explanation" - Student wants a concept explained or clarified
           Examples: "I don't understand X", "Can you explain Y?", "What does Z mean?"
        
        3. "quiz_request" - Student wants to be tested or practice
           Examples: "Test me", "Quiz me", "Ask me questions", "Am I ready?"
        
        4. "progress_inquiry" - Student wants to know their progress/performance
           Examples: "How am I doing?", "What's my progress?", "Am I improving?"
        
        5. "help_request" - Student needs general help or guidance
           Examples: "Help", "What can you do?", "I'm stuck", "I need assistance"
        
        6. "encouragement" - Student needs motivation or is expressing frustration
           Examples: "This is hard", "I'm struggling", "I can't do this", "I'm frustrated"
        
        7. "general_chat" - General conversation or unclear intent
           Examples: Greetings, casual conversation, unclear requests
        
        ANALYSIS FRAMEWORK:
        1. Analyze the student's message for keywords and emotional tone
        2. Consider the conversation context and current learning state
        3. Identify the most likely intent with confidence score
        4. Extract any specific concepts or topics mentioned
        5. Consider the student's learning preferences and background
        
        Respond with JSON:
        {{
            "intent": "most_likely_intent_category",
            "confidence": 0.85,
            "reasoning": "Why you chose this intent based on the message and context",
            "concept_to_explain": "specific concept if explanation intent",
            "emotional_tone": "positive|neutral|frustrated|confused",
            "suggested_response_approach": "how to best respond to this student",
            "context_relevance": "how current lesson context affects the response"
        }}
        
        Be precise in intent recognition - high confidence (>0.8) only when very clear, medium confidence (0.6-0.8) for likely intents, low confidence (<0.6) for unclear messages.
        """
    
    def _fallback_reasoning(self, context: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Fallback reasoning when agent services fail.
        """
        performance = context.get('latest_performance', {})
        score = performance.get('score', 0.7)
        
        if score < 0.6:
            decision = 'review'
        elif score > 0.8:
            decision = 'advance'
        else:
            decision = 'reinforce'
        
        return {
            'reasoning': 'Fallback decision based on performance score',
            'decision': decision,
            'confidence': 0.5,
            'next_actions': [f'{decision}_content'],
            'content_focus': 'Current topic',
            'difficulty_adjustment': 'same',
            'estimated_duration': 15
        }
    
    def _fallback_plan(self) -> List[Dict[str, Any]]:
        """
        Fallback learning plan when planning fails.
        """
        return [
            {
                'step': 1,
                'objective': 'Introduce concept',
                'difficulty': 'easy',
                'duration': 10
            },
            {
                'step': 2,
                'objective': 'Practice and reinforce',
                'difficulty': 'medium',
                'duration': 15
            },
            {
                'step': 3,
                'objective': 'Apply knowledge',
                'difficulty': 'hard',
                'duration': 20
            }
        ]
    
    async def _update_learning_patterns(self, memory_key: str) -> None:
        """
        Analyze experiences to identify learning patterns.
        """
        try:
            experiences = self.memory_store[memory_key]['experiences']
            
            if len(experiences) < 5:
                return  # Need more data
            
            # Analyze patterns (simplified)
            scores = []
            times = []
            decisions = []
            
            for exp in experiences[-10:]:  # Last 10 experiences
                exp_data = exp.get('experience', {})
                if 'score' in exp_data:
                    scores.append(exp_data['score'])
                if 'time_spent' in exp_data:
                    times.append(exp_data['time_spent'])
                if 'decision' in exp_data:
                    decisions.append(exp_data['decision'])
            
            # Update patterns
            patterns = self.memory_store[memory_key]['patterns']
            
            if scores:
                patterns['avg_score'] = sum(scores) / len(scores)
                patterns['score_trend'] = 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable'
            
            if times:
                patterns['avg_time'] = sum(times) / len(times)
            
            if decisions:
                patterns['common_decisions'] = list(set(decisions))
            
        except Exception as e:
            logging.error(f"Pattern update failed: {e}")
    
    async def _analyze_performance(self, **parameters) -> Dict[str, Any]:
        """
        Analyze performance data for decision making.
        """
        score = parameters.get('score', 0.7)
        time_spent = parameters.get('time_spent', 300)
        engagement = parameters.get('engagement_metrics', {})
        
        analysis = {
            'performance_level': 'struggling' if score < 0.6 else 'mastering' if score > 0.8 else 'learning',
            'time_efficiency': 'fast' if time_spent < 180 else 'slow' if time_spent > 420 else 'normal',
            'engagement_level': 'high' if engagement.get('focus_score', 0.7) > 0.8 else 'low' if engagement.get('focus_score', 0.7) < 0.5 else 'medium',
            'recommendations': []
        }
        
        # Add recommendations based on analysis
        if analysis['performance_level'] == 'struggling':
            analysis['recommendations'].append('Provide additional support and simpler explanations')
        if analysis['time_efficiency'] == 'slow':
            analysis['recommendations'].append('Break content into smaller chunks')
        if analysis['engagement_level'] == 'low':
            analysis['recommendations'].append('Increase interactivity and vary content format')
        
        return analysis
    
    async def _summarize_lesson(self, **parameters) -> str:
        """
        Generate a lesson summary using Bedrock Claude.
        """
        lesson_content = parameters.get('lesson_content', '')
        key_concepts = parameters.get('key_concepts', [])
        user_profile = parameters.get('user_profile', {})
        learning_progress = parameters.get('learning_progress', {})
        
        summary_prompt = f"""
        Create a concise, personalized summary of this lesson content:
        
        Lesson Content: {lesson_content[:2000]}
        Key Concepts: {', '.join(key_concepts)}
        
        User Context:
        - Learning Style: {user_profile.get('learning_style', 'visual')}
        - Progress: {learning_progress.get('completion_percentage', 0)}% complete
        
        Provide a summary that:
        1. Highlights the main concepts covered
        2. Shows how concepts connect to each other
        3. Relates to the user's learning style
        4. Encourages continued learning
        
        Keep it under 150 words and make it engaging.
        """
        
        try:
            response = await bedrock_service.invoke_claude(
                prompt=summary_prompt,
                max_tokens=300,
                temperature=0.5
            )
            return response.strip()
        except Exception as e:
            logging.error(f"Lesson summarization failed: {e}")
            if key_concepts:
                return f"Here's a quick summary: We've covered {', '.join(key_concepts[:3])}. These concepts build on each other to help you understand the core material. You're making great progress!"
            else:
                return "We've been working through important concepts that build your understanding step by step. Keep up the great work!"
    
    async def _explain_concept(self, **parameters) -> str:
        """
        Explain a specific concept using Bedrock Claude.
        """
        concept = parameters.get('concept', '')
        lesson_context = parameters.get('lesson_context', {})
        user_learning_style = parameters.get('user_learning_style', 'visual')
        user_background = parameters.get('user_background', {})
        
        explanation_prompt = f"""
        Explain the concept "{concept}" in a clear, personalized way.
        
        Context:
        - Current lesson: {lesson_context.get('title', 'Current lesson')}
        - User's learning style: {user_learning_style}
        - User's profession: {user_background.get('profession', 'general')}
        - Education level: {user_background.get('education_level', 'intermediate')}
        
        Provide an explanation that:
        1. Starts with a simple definition
        2. Uses examples relevant to their profession/background
        3. Adapts to their learning style:
           - Visual: Use analogies, metaphors, visual descriptions
           - Auditory: Use verbal explanations, discussions
           - Reading: Use detailed text, bullet points
           - Kinesthetic: Use hands-on examples, practical applications
        4. Connects to the current lesson context
        5. Ends with a question to check understanding
        
        Keep it under 200 words and make it engaging.
        """
        
        try:
            response = await bedrock_service.invoke_claude(
                prompt=explanation_prompt,
                max_tokens=400,
                temperature=0.6
            )
            return response.strip()
        except Exception as e:
            logging.error(f"Concept explanation failed: {e}")
            return f"Let me explain {concept}: This is an important concept that relates to what we're learning. Think of it as a building block that helps you understand the bigger picture. Would you like me to break it down further or give you a specific example?"
    
    async def _generate_practice_quiz(self, **parameters) -> Dict[str, Any]:
        """
        Generate a practice quiz using Bedrock Claude.
        """
        lesson_content = parameters.get('lesson_content', '')
        key_concepts = parameters.get('key_concepts', [])
        difficulty = parameters.get('difficulty', 'intermediate')
        num_questions = parameters.get('num_questions', 2)
        question_types = parameters.get('question_types', ['multiple_choice', 'true_false'])
        
        quiz_prompt = f"""
        Create a practice quiz based on this content:
        
        Content: {lesson_content[:1500]}
        Key Concepts: {', '.join(key_concepts)}
        
        Requirements:
        - {num_questions} questions
        - Difficulty: {difficulty}
        - Question types: {', '.join(question_types)}
        - Focus on understanding, not memorization
        
        Return JSON format:
        {{
            "questions": [
                {{
                    "question_id": "q1",
                    "question_type": "multiple_choice",
                    "question_text": "Question here?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = await bedrock_service.invoke_claude(
                prompt=quiz_prompt,
                max_tokens=800,
                temperature=0.4
            )
            
            # Parse JSON response
            quiz_data = json.loads(response.strip())
            return quiz_data
            
        except (json.JSONDecodeError, Exception) as e:
            logging.error(f"Practice quiz generation failed: {e}")
            # Fallback quiz
            return {
                "questions": [
                    {
                        "question_id": "q1",
                        "question_type": "multiple_choice",
                        "question_text": f"Which of these concepts have we been focusing on?",
                        "options": key_concepts[:4] if len(key_concepts) >= 4 else key_concepts + ["Other topics"],
                        "correct_answer": key_concepts[0] if key_concepts else "Main concept",
                        "explanation": "This is one of the key concepts we've been studying."
                    }
                ]
            }
    
    async def _show_progress(self, **parameters) -> str:
        """
        Show user progress summary.
        """
        user_id = parameters.get('user_id', '')
        current_lesson = parameters.get('current_lesson', {})
        learning_progress = parameters.get('learning_progress', {})
        recent_engagement = parameters.get('recent_engagement', [])
        
        # Calculate progress metrics
        completion_percentage = learning_progress.get('completion_percentage', 0)
        current_lesson_title = current_lesson.get('title', 'Current lesson')
        
        # Analyze recent performance
        quiz_events = [e for e in recent_engagement if e.get('event_type') == 'quiz_completed']
        if quiz_events:
            recent_scores = [e.get('event_data', {}).get('score', 0) for e in quiz_events[-3:]]
            avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        else:
            avg_score = 0
        
        progress_prompt = f"""
        Create an encouraging progress summary for a learner:
        
        Progress Data:
        - Current lesson: {current_lesson_title}
        - Completion: {completion_percentage:.1f}%
        - Recent quiz average: {avg_score:.1f}%
        - Total learning activities: {len(recent_engagement)}
        
        Provide a progress summary that:
        1. Celebrates their achievements
        2. Shows specific progress metrics
        3. Identifies areas of strength
        4. Provides gentle encouragement for improvement areas
        5. Suggests next steps
        
        Keep it positive, specific, and under 150 words.
        """
        
        try:
            response = await bedrock_service.invoke_claude(
                prompt=progress_prompt,
                max_tokens=300,
                temperature=0.6
            )
            return response.strip()
        except Exception as e:
            logging.error(f"Progress summary failed: {e}")
            # Fallback progress message
            if completion_percentage > 0:
                return f"Great progress! You've completed {completion_percentage:.1f}% of '{current_lesson_title}'. Your dedication to learning is showing - keep up the excellent work!"
            else:
                return "You're at the beginning of an exciting learning journey! Every step you take builds your knowledge and skills. Ready to dive in?"


class AdaptiveLearningAgent:
    """
    The autonomous brain of SnapStudy that makes intelligent decisions
    about learning paths without human intervention.
    
    Now powered by Amazon Bedrock AgentCore primitives for true autonomous reasoning.
    """
    
    def __init__(self):
        self.bedrock = bedrock_service
        self.db = db_service
        self.agent_core = BedrockAgentCore()  # AgentCore integration
        
        # Performance thresholds for adaptation decisions
        self.STRUGGLING_THRESHOLD = 0.60
        self.MASTERY_THRESHOLD = 0.80
        self.MIN_ENGAGEMENT_TIME = 30  # seconds
        self.MAX_MICRO_LESSON_DURATION = 15  # minutes
        
    async def start_adaptive_lesson(
        self, 
        user_id: str, 
        lesson_id: str
    ) -> Dict[str, Any]:
        """
        Initialize an adaptive learning session.
        This is the entry point for the autonomous learning loop.
        """
        try:
            logger.info(f"Starting adaptive lesson for user {user_id}, lesson {lesson_id}")
            
            # Get lesson and user context
            lesson = await self.db.get_lesson(lesson_id)
            if not lesson:
                raise ValueError(f"Lesson {lesson_id} not found")
            
            user = await self.db.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Verify lesson belongs to user
            if lesson['user_id'] != user_id:
                raise ValueError("Access denied: lesson does not belong to user")
            
            # Initialize learning session state
            session_state = {
                'session_id': str(uuid.uuid4()),
                'user_id': user_id,
                'lesson_id': lesson_id,
                'current_micro_lesson_index': 0,
                'total_micro_lessons': 0,
                'performance_history': [],
                'adaptation_history': [],
                'started_at': datetime.now(timezone.utc).isoformat(),
                'status': 'active'
            }
            
            # Get or generate micro-lessons
            micro_lessons = await self.db.get_lesson_micro_lessons(lesson_id)
            
            if not micro_lessons:
                # Generate initial micro-lessons from lesson content
                micro_lessons = await self._generate_initial_micro_lessons(lesson, user)
                session_state['total_micro_lessons'] = len(micro_lessons)
            else:
                session_state['total_micro_lessons'] = len(micro_lessons)
            
            # Get first micro-lesson
            first_micro_lesson = await self._get_next_micro_lesson(session_state, user)
            
            # Track engagement
            await self.db.track_engagement({
                'user_id': user_id,
                'event_type': 'adaptive_lesson_started',
                'event_data': {
                    'lesson_id': lesson_id,
                    'session_id': session_state['session_id'],
                    'total_micro_lessons': session_state['total_micro_lessons']
                }
            })
            
            return {
                'session_id': session_state['session_id'],
                'lesson': lesson,
                'current_micro_lesson': first_micro_lesson,
                'progress': {
                    'current_index': 0,
                    'total_micro_lessons': session_state['total_micro_lessons'],
                    'completion_percentage': 0.0
                },
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Failed to start adaptive lesson: {e}")
            raise ValueError(f"Failed to start adaptive lesson: {str(e)}")
    
    async def get_next_micro_lesson(
        self, 
        session_id: str, 
        user_id: str,
        previous_performance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Autonomous decision-making for the next micro-lesson.
        This is where the core adaptation logic happens.
        """
        try:
            logger.info(f"Getting next micro-lesson for session {session_id}")
            
            # Get current session state and user context
            context = await self._fetch_comprehensive_context(user_id, session_id)
            
            # Record previous performance if provided
            if previous_performance:
                await self._record_performance(session_id, previous_performance)
                context['latest_performance'] = previous_performance
            
            # CORE AUTONOMOUS DECISION MAKING
            adaptation_decision = await self._make_adaptation_decision(context)
            
            # Generate next micro-lesson based on decision
            next_micro_lesson = await self._generate_adaptive_micro_lesson(
                context, adaptation_decision
            )
            
            # Update session state
            await self._update_session_state(session_id, adaptation_decision, next_micro_lesson)
            
            # Track the autonomous decision
            await self.db.track_engagement({
                'user_id': user_id,
                'event_type': 'autonomous_adaptation',
                'event_data': {
                    'session_id': session_id,
                    'decision': adaptation_decision['decision'],
                    'reasoning': adaptation_decision['reasoning'],
                    'learning_state': adaptation_decision['learning_state']
                }
            })
            
            return {
                'micro_lesson': next_micro_lesson,
                'adaptation_info': {
                    'decision': adaptation_decision['decision'],
                    'reasoning': adaptation_decision['reasoning'],
                    'learning_state': adaptation_decision['learning_state']
                },
                'progress': context['progress'],
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get next micro-lesson: {e}")
            raise ValueError(f"Failed to get next micro-lesson: {str(e)}")
    
    async def submit_quiz_and_adapt(
        self, 
        session_id: str, 
        user_id: str,
        quiz_id: str,
        answers: Dict[str, str],
        time_spent: int,
        engagement_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process quiz submission and make autonomous adaptation decisions.
        """
        try:
            logger.info(f"Processing quiz submission for session {session_id}")
            
            # Get quiz and evaluate answers
            quiz = await self.db.get_quiz_by_id(quiz_id)
            if not quiz:
                raise ValueError(f"Quiz {quiz_id} not found")
            
            # Intelligent answer evaluation
            evaluation_results = await self._evaluate_quiz_answers(quiz, answers)
            
            # Calculate performance metrics
            performance_metrics = {
                'quiz_id': quiz_id,
                'score': evaluation_results['overall_score'],
                'correct_answers': evaluation_results['correct_count'],
                'total_questions': evaluation_results['total_questions'],
                'time_spent_seconds': time_spent,
                'engagement_metrics': engagement_metrics,
                'detailed_results': evaluation_results['question_results'],
                'submitted_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Get next micro-lesson with autonomous adaptation
            next_response = await self.get_next_micro_lesson(
                session_id, user_id, performance_metrics
            )
            
            # Generate detailed feedback
            feedback = await self._generate_performance_feedback(
                performance_metrics, evaluation_results
            )
            
            return {
                'quiz_results': {
                    'score': evaluation_results['overall_score'],
                    'feedback': feedback,
                    'detailed_results': evaluation_results['question_results']
                },
                'next_micro_lesson': next_response['micro_lesson'],
                'adaptation_info': next_response['adaptation_info'],
                'progress': next_response['progress']
            }
            
        except Exception as e:
            logger.error(f"Failed to process quiz submission: {e}")
            raise ValueError(f"Failed to process quiz submission: {str(e)}")
    
    async def _fetch_comprehensive_context(
        self, 
        user_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        Fetch all context needed for autonomous decision making.
        """
        # Get user profile and preferences
        user = await self.db.get_user_by_id(user_id)
        
        # Get recent engagement history
        engagement_history = await self.db.get_user_engagement(user_id, limit=20)
        
        # Get lesson progress
        # Note: In a real implementation, you'd store session state in DynamoDB
        # For now, we'll simulate this
        
        # Calculate learning patterns
        learning_patterns = self._analyze_learning_patterns(engagement_history)
        
        return {
            'user_profile': user,
            'engagement_history': engagement_history,
            'learning_patterns': learning_patterns,
            'session_id': session_id,
            'progress': {
                'current_index': 0,  # Would be retrieved from session state
                'total_micro_lessons': 5,  # Would be retrieved from session state
                'completion_percentage': 0.0
            }
        }
    
    async def _make_adaptation_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        CORE AUTONOMOUS DECISION MAKING LOGIC using AgentCore primitives.
        This is where the agent uses reasoning, memory, and planning to decide what to do next.
        """
        try:
            # Analyze current learning state
            learning_state = self._determine_learning_state(context)
            
            # Retrieve agent memory for this user
            user_id = context.get('user_profile', {}).get('user_id')
            if user_id:
                memory = await self.agent_core.retrieve_memory(user_id)
                context['agent_memory'] = memory
            
            # Use AgentCore reasoning over context
            decision_data = await self.agent_core.reason_over_context(
                context=context,
                goal="optimize_learning_path_based_on_performance_and_engagement"
            )
            
            # Validate and enhance decision
            validated_decision = self._validate_and_enhance_decision(
                decision_data, context, learning_state
            )
            
            # Update agent memory with this decision
            if user_id:
                await self.agent_core.update_memory(user_id, {
                    'decision': validated_decision['decision'],
                    'reasoning': validated_decision['reasoning'],
                    'context_summary': {
                        'learning_state': learning_state.value,
                        'performance': context.get('latest_performance', {}),
                        'user_profile': context.get('user_profile', {})
                    }
                })
            
            return validated_decision
            
        except Exception as e:
            logger.error(f"AgentCore decision making failed: {e}")
            # Fallback to safe default decision
            return self._fallback_decision(LearningState.LEARNING)
    
    def _create_decision_prompt(self, context: Dict[str, Any], learning_state: LearningState) -> str:
        """Create a comprehensive prompt for autonomous decision making."""
        
        user_profile = context['user_profile']
        latest_performance = context.get('latest_performance', {})
        learning_patterns = context['learning_patterns']
        
        prompt = f"""
        You are an autonomous adaptive learning agent. Analyze the learner's context and make the optimal decision for their next learning step.

        LEARNER CONTEXT:
        - Learning Style: {user_profile.get('learning_style', 'visual')}
        - Attention Span: {user_profile.get('attention_span', 15)} minutes
        - Difficulty Level: {user_profile.get('difficulty_level', 'intermediate')}
        - Current Learning State: {learning_state.value}
        
        RECENT PERFORMANCE:
        - Latest Quiz Score: {latest_performance.get('score', 'N/A')}%
        - Time Spent: {latest_performance.get('time_spent_seconds', 'N/A')} seconds
        - Engagement Level: {learning_patterns.get('avg_engagement', 'medium')}
        
        LEARNING PATTERNS:
        - Preferred Session Length: {learning_patterns.get('preferred_duration', 15)} minutes
        - Struggle Areas: {learning_patterns.get('struggle_areas', [])}
        - Strong Areas: {learning_patterns.get('strong_areas', [])}
        
        DECISION OPTIONS:
        - advance: Move to next concept (use when mastering current content)
        - review: Review current concept with different approach (use when struggling)
        - reinforce: Additional practice on current concept (use when partially understanding)
        - simplify: Reduce complexity (use when consistently struggling)
        - accelerate: Increase difficulty/pace (use when consistently excelling)
        - complete: Mark lesson as complete (use when all objectives met)

        Respond with JSON in this exact format:
        {{
            "decision": "advance|review|reinforce|simplify|accelerate|complete",
            "reasoning": "Clear explanation of why this decision was made",
            "confidence": 0.85,
            "next_topic_focus": "What specific aspect to focus on next",
            "difficulty_adjustment": "easier|same|harder",
            "estimated_duration": 12
        }}
        
        Make the decision that will optimize learning outcomes for this specific learner.
        """
        
        return prompt
    
    def _determine_learning_state(self, context: Dict[str, Any]) -> LearningState:
        """Analyze context to determine current learning state."""
        latest_performance = context.get('latest_performance', {})
        
        if not latest_performance:
            return LearningState.LEARNING
        
        score = latest_performance.get('score', 0.7)
        time_spent = latest_performance.get('time_spent_seconds', 300)
        engagement = latest_performance.get('engagement_metrics', {})
        
        # Determine state based on performance
        if score < self.STRUGGLING_THRESHOLD:
            return LearningState.STRUGGLING
        elif score > self.MASTERY_THRESHOLD:
            if time_spent < self.MIN_ENGAGEMENT_TIME:
                return LearningState.DISTRACTED
            else:
                return LearningState.MASTERING
        else:
            engagement_score = engagement.get('focus_score', 0.7)
            if engagement_score > 0.8:
                return LearningState.ENGAGED
            else:
                return LearningState.LEARNING
    
    def _analyze_learning_patterns(self, engagement_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical engagement to identify learning patterns."""
        if not engagement_history:
            return {
                'avg_engagement': 'medium',
                'preferred_duration': 15,
                'struggle_areas': [],
                'strong_areas': []
            }
        
        # Analyze patterns (simplified for now)
        quiz_events = [e for e in engagement_history if e.get('event_type') == 'quiz_completed']
        
        if quiz_events:
            avg_score = sum(e.get('event_data', {}).get('score', 0.7) for e in quiz_events) / len(quiz_events)
            engagement_level = 'high' if avg_score > 0.8 else 'medium' if avg_score > 0.6 else 'low'
        else:
            engagement_level = 'medium'
        
        return {
            'avg_engagement': engagement_level,
            'preferred_duration': 15,  # Would be calculated from actual data
            'struggle_areas': [],      # Would be identified from quiz results
            'strong_areas': []         # Would be identified from quiz results
        }
    
    def _validate_and_enhance_decision(
        self, 
        decision_data: Dict[str, Any], 
        context: Dict[str, Any], 
        learning_state: LearningState
    ) -> Dict[str, Any]:
        """Validate the AI decision and add safety checks."""
        
        # Ensure required fields exist
        decision = decision_data.get('decision', 'advance')
        if decision not in [d.value for d in AdaptationDecision]:
            decision = AdaptationDecision.ADVANCE.value
        
        # Add safety constraints
        if learning_state == LearningState.STRUGGLING and decision == 'accelerate':
            decision = AdaptationDecision.REVIEW.value
            decision_data['reasoning'] = "Overridden: Cannot accelerate when struggling"
        
        # Ensure reasonable duration
        duration = decision_data.get('estimated_duration', 15)
        duration = max(5, min(duration, self.MAX_MICRO_LESSON_DURATION))
        
        return {
            'decision': decision,
            'reasoning': decision_data.get('reasoning', 'Autonomous decision based on performance'),
            'confidence': decision_data.get('confidence', 0.8),
            'learning_state': learning_state.value,
            'next_topic_focus': decision_data.get('next_topic_focus', 'Continue current topic'),
            'difficulty_adjustment': decision_data.get('difficulty_adjustment', 'same'),
            'estimated_duration': duration
        }
    
    def _fallback_decision(self, learning_state: LearningState) -> Dict[str, Any]:
        """Provide a safe fallback decision when AI decision making fails."""
        return {
            'decision': AdaptationDecision.ADVANCE.value,
            'reasoning': 'Fallback decision due to processing error',
            'confidence': 0.5,
            'learning_state': learning_state.value,
            'next_topic_focus': 'Continue with next concept',
            'difficulty_adjustment': 'same',
            'estimated_duration': 15
        }
    
    async def _generate_adaptive_micro_lesson(
        self, 
        context: Dict[str, Any], 
        adaptation_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a micro-lesson based on the adaptation decision using AgentCore function invocation."""
        
        user_profile = context['user_profile']
        decision = adaptation_decision['decision']
        
        # Create content based on decision
        if decision == AdaptationDecision.REVIEW.value:
            content_type = "review_lesson"
            focus = "Review and reinforce previous concepts with different examples"
        elif decision == AdaptationDecision.SIMPLIFY.value:
            content_type = "simplified_lesson"
            focus = "Simplified explanation of current concept"
        elif decision == AdaptationDecision.ACCELERATE.value:
            content_type = "advanced_lesson"
            focus = "Advanced concepts and challenging examples"
        else:
            content_type = "standard_lesson"
            focus = adaptation_decision.get('content_focus', 'Continue learning')
        
        # Use AgentCore function invocation for micro-lesson generation
        micro_lesson = await self.agent_core.invoke_function(
            function_name="generate_micro_lesson",
            parameters={
                'topic_content': focus,
                'user_profile': user_profile,
                'sequence_number': context['progress']['current_index'] + 1,
                'total_lessons': context['progress']['total_micro_lessons']
            }
        )
        
        # Use AgentCore function invocation for quiz generation
        quiz = await self.agent_core.invoke_function(
            function_name="generate_quiz",
            parameters={
                'lesson_content': micro_lesson.get('content', ''),
                'difficulty_level': adaptation_decision.get('difficulty_adjustment', 'same'),
                'num_questions': 3
            }
        )
        
        # Store micro-lesson and quiz in database
        micro_lesson_record = await self.db.create_micro_lesson({
            'lesson_id': context.get('lesson_id', ''),
            'sequence_number': context['progress']['current_index'] + 1,
            'title': micro_lesson.get('title', 'Adaptive Lesson'),
            'content': micro_lesson.get('content', ''),
            'summary': micro_lesson.get('summary', ''),
            'key_concepts': micro_lesson.get('key_concepts', []),
            'estimated_duration_minutes': adaptation_decision['estimated_duration'],
            'difficulty_level': adaptation_decision.get('difficulty_adjustment', 'same'),
            'learning_objectives': micro_lesson.get('learning_objectives', []),
            'adaptation_type': decision
        })
        
        quiz_record = await self.db.create_quiz({
            'micro_lesson_id': micro_lesson_record['micro_lesson_id'],
            'questions': quiz.get('questions', []),
            'total_questions': quiz.get('total_questions', 3),
            'passing_score': quiz.get('passing_score', 0.7)
        })
        
        return {
            'micro_lesson_id': micro_lesson_record['micro_lesson_id'],
            'quiz_id': quiz_record['quiz_id'],
            'title': micro_lesson.get('title'),
            'content': micro_lesson.get('content'),
            'summary': micro_lesson.get('summary'),
            'key_concepts': micro_lesson.get('key_concepts', []),
            'estimated_duration': adaptation_decision['estimated_duration'],
            'quiz': quiz,
            'adaptation_type': decision
        }
    
    async def _evaluate_quiz_answers(
        self, 
        quiz: Dict[str, Any], 
        user_answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Intelligently evaluate quiz answers with partial credit using AgentCore function invocation."""
        
        questions = quiz.get('questions', [])
        question_results = []
        total_score = 0.0
        correct_count = 0
        
        for question in questions:
            question_id = question.get('question_id')
            user_answer = user_answers.get(question_id, '')
            
            # Use AgentCore function invocation for intelligent evaluation
            evaluation = await self.agent_core.invoke_function(
                function_name="evaluate_answer",
                parameters={
                    'question': question,
                    'user_answer': user_answer
                }
            )
            
            question_results.append({
                'question_id': question_id,
                'user_answer': user_answer,
                'correct_answer': question.get('correct_answer'),
                'is_correct': evaluation.get('is_correct', False),
                'score': evaluation.get('score', 0.0),
                'feedback': evaluation.get('feedback', ''),
                'suggestions': evaluation.get('suggestions', '')
            })
            
            total_score += evaluation.get('score', 0.0)
            if evaluation.get('is_correct', False):
                correct_count += 1
        
        overall_score = (total_score / len(questions)) * 100 if questions else 0
        
        return {
            'overall_score': overall_score,
            'total_questions': len(questions),
            'correct_count': correct_count,
            'question_results': question_results
        }
    
    async def _generate_performance_feedback(
        self, 
        performance_metrics: Dict[str, Any], 
        evaluation_results: Dict[str, Any]
    ) -> str:
        """Generate personalized feedback based on performance."""
        
        score = performance_metrics['score']
        time_spent = performance_metrics['time_spent_seconds']
        
        feedback_prompt = f"""
        Generate encouraging, personalized feedback for a learner based on their quiz performance:
        
        Performance:
        - Score: {score}%
        - Time spent: {time_spent} seconds
        - Correct answers: {evaluation_results['correct_count']}/{evaluation_results['total_questions']}
        
        Provide:
        1. Positive reinforcement
        2. Specific areas of strength
        3. Gentle guidance for improvement areas
        4. Encouragement to continue learning
        
        Keep it concise (2-3 sentences) and motivating.
        """
        
        feedback = await self.bedrock.invoke_claude(
            prompt=feedback_prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        return feedback.strip()
    
    async def _generate_initial_micro_lessons(
        self, 
        lesson: Dict[str, Any], 
        user: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate initial micro-lessons when starting a new lesson."""
        
        # This would typically analyze the lesson content and break it down
        # For now, we'll create a placeholder structure
        
        micro_lessons = []
        for i in range(3):  # Generate 3 initial micro-lessons
            micro_lesson = await self.bedrock.generate_micro_lesson(
                topic_content=lesson.get('description', 'Learning content'),
                user_profile=user,
                sequence_number=i + 1,
                total_lessons=3
            )
            
            micro_lesson_record = await self.db.create_micro_lesson({
                'lesson_id': lesson['lesson_id'],
                'sequence_number': i + 1,
                'title': micro_lesson.get('title', f'Lesson {i + 1}'),
                'content': micro_lesson.get('content', ''),
                'summary': micro_lesson.get('summary', ''),
                'key_concepts': micro_lesson.get('key_concepts', []),
                'estimated_duration_minutes': micro_lesson.get('estimated_duration_minutes', 15),
                'difficulty_level': user.get('difficulty_level', 'intermediate'),
                'learning_objectives': micro_lesson.get('learning_objectives', [])
            })
            
            micro_lessons.append(micro_lesson_record)
        
        return micro_lessons
    
    async def _get_next_micro_lesson(
        self, 
        session_state: Dict[str, Any], 
        user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get the next micro-lesson for the session."""
        
        lesson_id = session_state['lesson_id']
        micro_lessons = await self.db.get_lesson_micro_lessons(lesson_id)
        
        if not micro_lessons:
            # Generate first micro-lesson
            lesson = await self.db.get_lesson(lesson_id)
            micro_lessons = await self._generate_initial_micro_lessons(lesson, user)
        
        # Return first micro-lesson
        if micro_lessons:
            first_lesson = micro_lessons[0]
            
            # Generate quiz for this micro-lesson
            quiz = await self.bedrock.generate_quiz(
                lesson_content=first_lesson.get('content', ''),
                difficulty_level=user.get('difficulty_level', 'intermediate'),
                num_questions=3
            )
            
            quiz_record = await self.db.create_quiz({
                'micro_lesson_id': first_lesson['micro_lesson_id'],
                'questions': quiz.get('questions', []),
                'total_questions': quiz.get('total_questions', 3),
                'passing_score': quiz.get('passing_score', 0.7)
            })
            
            return {
                'micro_lesson_id': first_lesson['micro_lesson_id'],
                'quiz_id': quiz_record['quiz_id'],
                'title': first_lesson.get('title'),
                'content': first_lesson.get('content'),
                'summary': first_lesson.get('summary'),
                'key_concepts': first_lesson.get('key_concepts', []),
                'estimated_duration': first_lesson.get('estimated_duration_minutes', 15),
                'quiz': quiz
            }
        
        return {}
    
    async def _record_performance(
        self, 
        session_id: str, 
        performance: Dict[str, Any]
    ) -> None:
        """Record performance data for future decision making."""
        
        # In a real implementation, this would store session state in DynamoDB
        # For now, we'll track it as engagement data
        
        await self.db.track_engagement({
            'user_id': performance.get('user_id', ''),
            'event_type': 'quiz_completed',
            'event_data': {
                'session_id': session_id,
                'quiz_id': performance.get('quiz_id'),
                'score': performance.get('score'),
                'time_spent': performance.get('time_spent_seconds'),
                'engagement_metrics': performance.get('engagement_metrics', {})
            }
        })
    
    async def _update_session_state(
        self, 
        session_id: str, 
        adaptation_decision: Dict[str, Any], 
        micro_lesson: Dict[str, Any]
    ) -> None:
        """Update session state after generating new content."""
        
        # In a real implementation, this would update session state in DynamoDB
        # For now, we'll track the adaptation decision
        
        await self.db.track_engagement({
            'user_id': '',  # Would be retrieved from session
            'event_type': 'adaptation_decision',
            'event_data': {
                'session_id': session_id,
                'decision': adaptation_decision['decision'],
                'reasoning': adaptation_decision['reasoning'],
                'micro_lesson_id': micro_lesson.get('micro_lesson_id')
            }
        })


# Global service instance
adaptive_agent = AdaptiveLearningAgent()