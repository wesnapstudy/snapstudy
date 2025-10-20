import React, { useState, useEffect } from 'react';
import { AudioLesson, VideoLesson } from '../types';
import multimediaService from '../services/multimediaService';
import MultimediaPlayer from './MultimediaPlayer';
import './MultimediaLibrary.css';

interface MultimediaLibraryProps {
  onLessonSelect?: (lesson: AudioLesson | VideoLesson, type: 'audio' | 'video') => void;
  selectedLessonId?: string;
  showPlayer?: boolean;
}

const MultimediaLibrary: React.FC<MultimediaLibraryProps> = ({
  onLessonSelect,
  selectedLessonId,
  showPlayer = true
}) => {
  const [audioLessons, setAudioLessons] = useState<AudioLesson[]>([]);
  const [videoLessons, setVideoLessons] = useState<VideoLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<{
    lesson: AudioLesson | VideoLesson;
    type: 'audio' | 'video';
  } | null>(null);
  const [filter, setFilter] = useState<'all' | 'audio' | 'video'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'duration'>('date');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadMultimediaLibrary();
  }, []);

  const loadMultimediaLibrary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const library = await multimediaService.getUserMultimediaLessons();
      setAudioLessons(library.audio.lessons);
      setVideoLessons(library.video.lessons);
      
    } catch (error) {
      console.error('Error loading multimedia library:', error);
      setError('Failed to load multimedia library. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLessonClick = (lesson: AudioLesson | VideoLesson, type: 'audio' | 'video') => {
    const selection = { lesson, type };
    setSelectedLesson(selection);
    
    if (onLessonSelect) {
      onLessonSelect(lesson, type);
    }

    // Track engagement
    multimediaService.trackMultimediaEvent(
      `${type}_lesson_selected`,
      type === 'audio' ? (lesson as AudioLesson).audio_lesson_id : (lesson as VideoLesson).video_lesson_id,
      { title: lesson.title }
    );
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getFilteredAndSortedLessons = () => {
    let lessons: Array<{ lesson: AudioLesson | VideoLesson; type: 'audio' | 'video' }> = [];
    
    // Filter by type
    if (filter === 'all' || filter === 'audio') {
      lessons.push(...audioLessons.map(lesson => ({ lesson, type: 'audio' as const })));
    }
    if (filter === 'all' || filter === 'video') {
      lessons.push(...videoLessons.map(lesson => ({ lesson, type: 'video' as const })));
    }

    // Filter by search term
    if (searchTerm) {
      lessons = lessons.filter(({ lesson }) =>
        lesson.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort lessons
    lessons.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.lesson.title.localeCompare(b.lesson.title);
        case 'duration':
          return b.lesson.duration_seconds - a.lesson.duration_seconds;
        case 'date':
        default:
          return new Date(b.lesson.generated_at).getTime() - new Date(a.lesson.generated_at).getTime();
      }
    });

    return lessons;
  };

  const filteredLessons = getFilteredAndSortedLessons();
  const totalLessons = audioLessons.length + videoLessons.length;

  if (loading) {
    return (
      <div className="multimedia-library loading">
        <div className="loading-spinner"></div>
        <p>Loading your multimedia library...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="multimedia-library error">
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <div className="error-content">
            <h3>Error Loading Library</h3>
            <p>{error}</p>
            <button className="retry-button" onClick={loadMultimediaLibrary}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (totalLessons === 0) {
    return (
      <div className="multimedia-library empty">
        <div className="empty-state">
          <div className="empty-icon">🎵</div>
          <h3>No Multimedia Content Yet</h3>
          <p>Generate audio or video lessons from your text content to build your multimedia library.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="multimedia-library">
      {/* Header */}
      <div className="library-header">
        <div className="header-content">
          <h2>🎵 Multimedia Library</h2>
          <div className="library-stats">
            <span className="stat">
              <span className="stat-value">{audioLessons.length}</span>
              <span className="stat-label">Audio</span>
            </span>
            <span className="stat">
              <span className="stat-value">{videoLessons.length}</span>
              <span className="stat-label">Video</span>
            </span>
            <span className="stat">
              <span className="stat-value">{totalLessons}</span>
              <span className="stat-label">Total</span>
            </span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="library-controls">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search multimedia lessons..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="search-icon">🔍</div>
        </div>

        <div className="filter-controls">
          <div className="filter-group">
            <label>Filter:</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'audio' | 'video')}
            >
              <option value="all">All Content</option>
              <option value="audio">Audio Only</option>
              <option value="video">Video Only</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'title' | 'duration')}
            >
              <option value="date">Date Created</option>
              <option value="title">Title</option>
              <option value="duration">Duration</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="library-content">
        {/* Lessons List */}
        <div className="lessons-list">
          {filteredLessons.length === 0 ? (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h3>No lessons found</h3>
              <p>Try adjusting your search or filter criteria.</p>
            </div>
          ) : (
            <div className="lessons-grid">
              {filteredLessons.map(({ lesson, type }, index) => (
                <div
                  key={`${type}-${type === 'audio' ? (lesson as AudioLesson).audio_lesson_id : (lesson as VideoLesson).video_lesson_id}`}
                  className={`lesson-card ${type} ${
                    selectedLesson && 
                    ((type === 'audio' && selectedLesson.lesson === lesson) ||
                     (type === 'video' && selectedLesson.lesson === lesson))
                      ? 'selected' : ''
                  }`}
                  onClick={() => handleLessonClick(lesson, type)}
                >
                  <div className="lesson-header">
                    <div className="lesson-type">
                      <div className={`type-icon ${type}`}>
                        {type === 'audio' ? '🎵' : '🎥'}
                      </div>
                      <span className="type-label">{type.toUpperCase()}</span>
                    </div>
                    <div className="lesson-duration">
                      {formatDuration(lesson.duration_seconds)}
                    </div>
                  </div>

                  <div className="lesson-content">
                    <h3 className="lesson-title">{lesson.title}</h3>
                    
                    <div className="lesson-metadata">
                      <div className="metadata-item">
                        <span className="metadata-label">Created:</span>
                        <span className="metadata-value">{formatDate(lesson.generated_at)}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-label">Size:</span>
                        <span className="metadata-value">{formatFileSize(lesson.file_size_bytes)}</span>
                      </div>
                      {type === 'audio' && (
                        <div className="metadata-item">
                          <span className="metadata-label">Voice:</span>
                          <span className="metadata-value">{(lesson as AudioLesson).voice_profile.VoiceId}</span>
                        </div>
                      )}
                      {type === 'video' && (
                        <div className="metadata-item">
                          <span className="metadata-label">Quality:</span>
                          <span className="metadata-value">{(lesson as VideoLesson).resolution}</span>
                        </div>
                      )}
                    </div>

                    {type === 'audio' && (lesson as AudioLesson).key_timestamps && (
                      <div className="lesson-features">
                        <span className="feature-tag">
                          📚 {(lesson as AudioLesson).key_timestamps.length} Chapters
                        </span>
                        <span className="feature-tag">📝 Transcript</span>
                      </div>
                    )}

                    {type === 'video' && (lesson as VideoLesson).interactive_elements && (
                      <div className="lesson-features">
                        <span className="feature-tag">
                          🎯 {(lesson as VideoLesson).interactive_elements.length} Interactive Elements
                        </span>
                        {(lesson as VideoLesson).scenes && (
                          <span className="feature-tag">
                            🎬 {(lesson as VideoLesson).scenes.length} Scenes
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="lesson-actions">
                    <button className="play-button">
                      ▶️ Play
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Player */}
        {showPlayer && selectedLesson && (
          <div className="player-section">
            <div className="player-header">
              <h3>Now Playing: {selectedLesson.lesson.title}</h3>
              <button 
                className="close-player"
                onClick={() => setSelectedLesson(null)}
                aria-label="Close player"
              >
                ✕
              </button>
            </div>
            <MultimediaPlayer
              audioLesson={selectedLesson.type === 'audio' ? selectedLesson.lesson as AudioLesson : undefined}
              videoLesson={selectedLesson.type === 'video' ? selectedLesson.lesson as VideoLesson : undefined}
              onComplete={() => {
                multimediaService.trackMultimediaEvent(
                  `${selectedLesson.type}_lesson_completed`,
                  selectedLesson.type === 'audio' 
                    ? (selectedLesson.lesson as AudioLesson).audio_lesson_id 
                    : (selectedLesson.lesson as VideoLesson).video_lesson_id
                );
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default MultimediaLibrary;