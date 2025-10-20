"""
Test suite for multimedia content generation services.

Tests audio and video generation functionality with mock AWS services.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from src.services.audio_generation import AudioMicroLessonGenerator
from src.services.video_generation import VideoMicroLessonGenerator
from src.services.adaptive_agent import AdaptiveLearningAgent


class TestAudioGeneration:
    """Test audio micro-lesson generation."""
    
    @pytest.fixture
    def audio_service(self):
        """Create audio generation service with mocked dependencies."""
        with patch('src.services.audio_generation.boto3.client'), \
             patch('src.services.audio_generation.bedrock_service'), \
             patch('src.services.audio_generation.db_service'):
            return AudioMicroLessonGenerator()
    
    @pytest.fixture
    def sample_text_lesson(self):
        """Sample text lesson for testing."""
        return {
            'micro_lesson_id': 'lesson-123',
            'title': 'Introduction to Machine Learning',
            'content': 'Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.',
            'key_concepts': ['machine learning', 'artificial intelligence', 'data'],
            'learning_objectives': ['Understand ML basics', 'Identify AI applications']
        }
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing."""
        return {
            'user_id': 'user-456',
            'learning_style': 'auditory',
            'attention_span': 10,
            'voice_preference': 'professional_female',
            'tone_preference': 'professional',
            'speaking_rate': 'medium',
            'profession': 'software engineer'
        }
    
    @pytest.mark.asyncio
    async def test_voice_profile_selection(self, audio_service, sample_user_profile):
        """Test voice profile selection based on user preferences."""
        voice_config = await audio_service._select_voice_profile(sample_user_profile)
        
        assert voice_config['VoiceId'] == 'Joanna'  # professional_female
        assert voice_config['Engine'] == 'neural'
        assert voice_config['LanguageCode'] == 'en-US'
        assert voice_config['speaking_rate'] == 'medium'
    
    @pytest.mark.asyncio
    async def test_text_optimization_for_speech(self, audio_service, sample_text_lesson, sample_user_profile):
        """Test text optimization for speech synthesis."""
        # Mock Bedrock response
        mock_response = {
            "introduction": "Welcome to this lesson on machine learning.",
            "main_content": "Machine learning is a powerful technology that enables computers to learn from data.",
            "conclusion": "This concludes our introduction to machine learning.",
            "full_text": "Welcome to this lesson on machine learning. Machine learning is a powerful technology that enables computers to learn from data. This concludes our introduction to machine learning.",
            "emphasis_points": ["machine learning", "artificial intelligence"],
            "pause_markers": [30, 60],
            "estimated_speech_duration": 120
        }
        
        with patch.object(audio_service.bedrock, 'invoke_claude', return_value=json.dumps(mock_response)):
            result = await audio_service._optimize_text_for_speech(sample_text_lesson, sample_user_profile)
            
            assert result['introduction'] == mock_response['introduction']
            assert result['main_content'] == mock_response['main_content']
            assert 'machine learning' in result['emphasis_points']
            assert len(result['pause_markers']) == 2
    
    @pytest.mark.asyncio
    async def test_ssml_markup_generation(self, audio_service, sample_user_profile):
        """Test SSML markup generation for enhanced speech."""
        speech_content = {
            "introduction": "Welcome to this lesson",
            "main_content": "This is the main content with machine learning concepts",
            "conclusion": "Thank you for learning",
            "emphasis_points": ["machine learning"],
            "pause_markers": [30]
        }
        
        voice_config = {
            'VoiceId': 'Joanna',
            'Engine': 'neural',
            'volume': 'medium'
        }
        
        ssml = await audio_service._generate_ssml_markup(speech_content, sample_user_profile, voice_config)
        
        assert '<speak>' in ssml
        assert '</speak>' in ssml
        assert '<prosody rate="medium"' in ssml
        assert '<emphasis level="strong">machine learning</emphasis>' in ssml
        assert '<break time="0.5s"/>' in ssml
    
    @pytest.mark.asyncio
    async def test_polly_speech_synthesis(self, audio_service):
        """Test Polly speech synthesis with mocked response."""
        mock_audio_stream = Mock()
        mock_audio_stream.read.return_value = b'fake_audio_data'
        
        mock_response = {
            'AudioStream': mock_audio_stream,
            'ContentType': 'audio/mpeg',
            'RequestCharacters': 100
        }
        
        audio_service.polly_client.synthesize_speech.return_value = mock_response
        
        ssml_content = '<speak>Test content</speak>'
        voice_config = {'VoiceId': 'Joanna', 'Engine': 'neural', 'LanguageCode': 'en-US'}
        
        result = await audio_service._synthesize_speech(ssml_content, voice_config)
        
        assert result['audio_data'] == b'fake_audio_data'
        assert result['content_type'] == 'audio/mpeg'
        assert result['request_characters'] == 100
        assert result['file_size'] == len(b'fake_audio_data')
    
    @pytest.mark.asyncio
    async def test_full_audio_generation_workflow(self, audio_service, sample_text_lesson, sample_user_profile):
        """Test complete audio generation workflow."""
        # Mock all external dependencies
        with patch.object(audio_service.bedrock, 'invoke_claude') as mock_bedrock, \
             patch.object(audio_service, '_synthesize_speech') as mock_synthesis, \
             patch.object(audio_service, '_store_audio_file') as mock_store, \
             patch.object(audio_service, '_store_audio_lesson_metadata') as mock_metadata:
            
            # Setup mocks
            mock_bedrock.return_value = json.dumps({
                "introduction": "Welcome",
                "main_content": "Content",
                "conclusion": "Conclusion",
                "full_text": "Welcome Content Conclusion",
                "emphasis_points": ["machine learning"],
                "pause_markers": [30],
                "estimated_speech_duration": 120
            })
            
            mock_synthesis.return_value = {
                'audio_data': b'fake_audio',
                'content_type': 'audio/mpeg',
                'duration': 120,
                'file_size': 1024
            }
            
            mock_store.return_value = 'https://s3.amazonaws.com/bucket/audio.mp3'
            mock_metadata.return_value = None
            
            # Execute test
            result = await audio_service.generate_audio_micro_lesson(
                sample_text_lesson, sample_user_profile
            )
            
            # Verify results
            assert result['audio_lesson_id'] is not None
            assert result['title'] == sample_text_lesson['title']
            assert result['audio_url'] == 'https://s3.amazonaws.com/bucket/audio.mp3'
            assert result['duration_seconds'] == 120
            assert result['voice_profile']['VoiceId'] == 'Joanna'
            assert 'generated_at' in result


class TestVideoGeneration:
    """Test video micro-lesson generation."""
    
    @pytest.fixture
    def video_service(self):
        """Create video generation service with mocked dependencies."""
        with patch('src.services.video_generation.boto3.client'), \
             patch('src.services.video_generation.bedrock_service'), \
             patch('src.services.video_generation.db_service'), \
             patch('src.services.video_generation.audio_generation_service'):
            return VideoMicroLessonGenerator()
    
    @pytest.fixture
    def sample_text_lesson(self):
        """Sample text lesson for testing."""
        return {
            'micro_lesson_id': 'lesson-123',
            'title': 'Data Structures Overview',
            'content': 'Data structures are ways of organizing and storing data in a computer so that it can be accessed and modified efficiently.',
            'key_concepts': ['data structures', 'arrays', 'linked lists'],
            'learning_objectives': ['Understand data organization', 'Compare different structures']
        }
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing."""
        return {
            'user_id': 'user-789',
            'learning_style': 'visual',
            'profession': 'software engineer',
            'visual_style_preference': 'technical'
        }
    
    def test_visual_style_selection(self, video_service, sample_user_profile):
        """Test visual style selection based on user profile."""
        style = video_service._select_visual_style(sample_user_profile)
        
        assert style['style'] == 'modern, technical, high-tech'
        assert 'dark theme' in style['color_scheme']
        assert 'tech environment' in style['background']
    
    @pytest.mark.asyncio
    async def test_video_script_creation(self, video_service, sample_text_lesson, sample_user_profile):
        """Test video script creation from text lesson."""
        mock_script = {
            "title": "Data Structures Overview",
            "total_duration_seconds": 180,
            "introduction": {
                "narration": "Welcome to data structures",
                "visual_description": "Title card with data structure diagrams",
                "duration_seconds": 15
            },
            "main_scenes": [
                {
                    "scene_number": 1,
                    "narration": "Data structures organize information",
                    "visual_description": "Animated diagrams showing arrays and lists",
                    "duration_seconds": 120,
                    "visual_elements": ["diagrams", "animations"],
                    "key_concepts": ["data structures"]
                }
            ],
            "conclusion": {
                "narration": "Summary of key concepts",
                "visual_description": "Summary slide",
                "duration_seconds": 45
            }
        }
        
        with patch.object(video_service.bedrock, 'invoke_claude', return_value=json.dumps(mock_script)):
            result = await video_service._create_video_script(
                sample_text_lesson, sample_user_profile
            )
            
            assert result['title'] == mock_script['title']
            assert result['total_duration_seconds'] == 180
            assert len(result['main_scenes']) == 1
            assert 'data structures' in result['main_scenes'][0]['key_concepts']
    
    @pytest.mark.asyncio
    async def test_nova_prompt_creation(self, video_service):
        """Test Nova Reel prompt creation."""
        scene_config = {
            'scene_type': 'main_content',
            'description': 'Show data structure diagrams',
            'visual_elements': ['diagrams', 'animations'],
            'key_concepts': ['arrays', 'linked lists'],
            'duration': 30,
            'style': {
                'style': 'technical and modern',
                'color_scheme': 'dark theme with blue accents',
                'background': 'tech environment'
            }
        }
        
        adaptations = {'animation_speed': 'moderate'}
        
        prompt = video_service._create_nova_prompt(scene_config, adaptations)
        
        assert 'moderate paced educational video' in prompt
        assert 'technical and modern' in prompt
        assert 'data structure diagrams' in prompt
        assert 'arrays, linked lists' in prompt
        assert '30 seconds' in prompt
    
    @pytest.mark.asyncio
    async def test_single_scene_generation(self, video_service):
        """Test single scene generation with Nova Reel."""
        scene_config = {
            'scene_type': 'introduction',
            'description': 'Welcome scene with title',
            'duration': 15
        }
        
        adaptations = {'animation_speed': 'moderate'}
        
        # Mock Nova Reel response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'videoDataUri': 'data:video/mp4;base64,ZmFrZV92aWRlb19kYXRh'  # "fake_video_data" in base64
        }).encode()
        
        video_service.bedrock_client.invoke_model.return_value = mock_response
        
        result = await video_service._generate_single_scene(scene_config, adaptations)
        
        assert result['scene_type'] == 'introduction'
        assert result['duration'] == 15
        assert result['generated_successfully'] is True
        assert 'video_data' in result
    
    @pytest.mark.asyncio
    async def test_interactive_elements_generation(self, video_service, sample_text_lesson, sample_user_profile):
        """Test interactive elements generation for video."""
        elements = video_service._generate_interactive_elements(sample_text_lesson, sample_user_profile)
        
        # Should have pause point, knowledge check, and summary review
        assert len(elements) >= 3
        
        pause_point = next((e for e in elements if e['type'] == 'pause_point'), None)
        assert pause_point is not None
        assert pause_point['time_seconds'] == 60
        
        knowledge_check = next((e for e in elements if e['type'] == 'knowledge_check'), None)
        assert knowledge_check is not None
        assert 'data structures' in knowledge_check['description']


class TestMultiModalIntegration:
    """Test multi-modal content generation integration."""
    
    @pytest.fixture
    def adaptive_agent(self):
        """Create adaptive agent with mocked dependencies."""
        with patch('src.services.adaptive_agent.bedrock_service'), \
             patch('src.services.adaptive_agent.db_service'), \
             patch('src.services.adaptive_agent.audio_generation_service'), \
             patch('src.services.adaptive_agent.video_generation_service'):
            return AdaptiveLearningAgent()
    
    @pytest.mark.asyncio
    async def test_multi_modal_lesson_generation(self, adaptive_agent):
        """Test complete multi-modal lesson generation."""
        lesson_content = "Introduction to Python programming fundamentals"
        user_profile = {
            'user_id': 'user-123',
            'learning_style': 'visual',
            'profession': 'developer'
        }
        content_types = ['text', 'audio', 'video']
        
        # Mock text lesson generation
        mock_text_lesson = {
            'micro_lesson_id': 'lesson-456',
            'title': 'Python Fundamentals',
            'content': 'Python is a programming language...',
            'key_concepts': ['python', 'programming']
        }
        
        # Mock audio lesson generation
        mock_audio_lesson = {
            'audio_lesson_id': 'audio-789',
            'audio_url': 'https://s3.../audio.mp3',
            'duration_seconds': 180
        }
        
        # Mock video lesson generation
        mock_video_lesson = {
            'video_lesson_id': 'video-101',
            'video_url': 'https://s3.../video.mp4',
            'duration_seconds': 200
        }
        
        with patch('src.services.adaptive_agent.bedrock_service.generate_micro_lesson', return_value=mock_text_lesson), \
             patch('src.services.adaptive_agent.audio_generation_service.generate_audio_micro_lesson', return_value=mock_audio_lesson), \
             patch('src.services.adaptive_agent.video_generation_service.generate_video_micro_lesson', return_value=mock_video_lesson), \
             patch('src.services.adaptive_agent.db_service.put_item'), \
             patch('src.services.adaptive_agent.db_service.track_engagement'):
            
            result = await adaptive_agent.generate_multi_modal_micro_lesson(
                lesson_content, user_profile, 1, 5, content_types
            )
            
            assert result['lesson_id'] is not None
            assert result['generated_formats'] == ['text', 'audio', 'video']
            assert result['text_lesson'] == mock_text_lesson
            assert result['audio_lesson'] == mock_audio_lesson
            assert result['video_lesson'] == mock_video_lesson
            assert result['user_id'] == 'user-123'


class TestMultimediaAPI:
    """Test multimedia API endpoints."""
    
    @pytest.mark.asyncio
    async def test_audio_generation_request_validation(self):
        """Test audio generation request validation."""
        from src.api.routers.multimedia import AudioGenerationRequest
        
        # Valid request
        valid_request = AudioGenerationRequest(
            text_lesson_id="lesson-123",
            voice_preference="professional_female",
            tone_preference="professional"
        )
        
        assert valid_request.text_lesson_id == "lesson-123"
        assert valid_request.voice_preference == "professional_female"
        assert valid_request.tone_preference == "professional"
        assert valid_request.speaking_rate == "medium"  # default
    
    @pytest.mark.asyncio
    async def test_video_generation_request_validation(self):
        """Test video generation request validation."""
        from src.api.routers.multimedia import VideoGenerationRequest
        
        # Valid request
        valid_request = VideoGenerationRequest(
            text_lesson_id="lesson-456",
            visual_style="technical",
            include_narration=True
        )
        
        assert valid_request.text_lesson_id == "lesson-456"
        assert valid_request.visual_style == "technical"
        assert valid_request.include_narration is True
        assert valid_request.include_subtitles is True  # default
    
    @pytest.mark.asyncio
    async def test_multimodal_generation_request_validation(self):
        """Test multi-modal generation request validation."""
        from src.api.routers.multimedia import MultiModalGenerationRequest
        
        # Valid request
        valid_request = MultiModalGenerationRequest(
            lesson_content="Test content",
            content_types=["text", "audio", "video"],
            user_preferences={"learning_style": "visual"}
        )
        
        assert valid_request.lesson_content == "Test content"
        assert valid_request.content_types == ["text", "audio", "video"]
        assert valid_request.user_preferences["learning_style"] == "visual"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])