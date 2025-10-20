import React, { useState } from 'react';
import { Lesson, MicroLesson, AudioLesson, VideoLesson } from '../types';
import MultimediaGenerator from './MultimediaGenerator';
import MultimediaPlayer from './MultimediaPlayer';
import multimediaService from '../services/multimediaService';
import './LessonViewer.css';

interface LessonViewerProps {
  lesson: Lesson | null;
  microLessons: MicroLesson[];
  onQuizStart?: (lessonId: string) => void;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson, microLessons, onQuizStart }) => {
  const [selectedMicroLesson, setSelectedMicroLesson] = useState<MicroLesson | null>(
    microLessons.length > 0 ? microLessons[0] : null
  );
  const [showMultimediaGenerator, setShowMultimediaGenerator] = useState(false);
  const [audioLesson, setAudioLesson] = useState<AudioLesson | null>(null);
  const [videoLesson, setVideoLesson] = useState<VideoLesson | null>(null);
  const [multimediaView, setMultimediaView] = useState<'text' | 'audio' | 'video'>('text');

  React.useEffect(() => {
    if (microLessons.length > 0) {
      setSelectedMicroLesson(microLessons[0]);
    }
  }, [microLessons]);

  React.useEffect(() => {
    // Reset multimedia content when lesson changes
    setAudioLesson(null);
    setVideoLesson(null);
    setMultimediaView('text');
  }, [lesson]);

  const handleMultimediaGeneration = async (type: 'audio' | 'video', lessonId: string) => {
    try {
      if (type === 'audio') {
        const audio = await multimediaService.getAudioLesson(lessonId);
        setAudioLesson(audio);
        setMultimediaView('audio');
      } else {
        const video = await multimediaService.getVideoLesson(lessonId);
        setVideoLesson(video);
        setMultimediaView('video');
      }
      setShowMultimediaGenerator(false);
    } catch (error) {
      console.error('Error loading multimedia lesson:', error);
    }
  };

  const handleQuizStart = () => {
    if (onQuizStart && selectedMicroLesson) {
      onQuizStart(selectedMicroLesson.micro_lesson_id);
    }
  };

  if (!lesson) {
    return (
      <div className="lesson-viewer">
        <div className="empty-viewer">
          <div className="empty-icon">📖</div>
          <h3>Select a lesson to start learning</h3>
          <p>Choose a lesson from your library or upload a new document to get started.</p>
        </div>
      </div>
    );
  }

  if (lesson.status === 'processing') {
    return (
      <div className="lesson-viewer">
        <div className="processing-state">
          <div className="loading-spinner"></div>
          <h3>Processing your lesson...</h3>
          <p>We're breaking down "{lesson.title}" into bite-sized micro-lessons. This usually takes a few minutes.</p>
        </div>
      </div>
    );
  }

  if (lesson.status === 'failed') {
    return (
      <div className="lesson-viewer">
        <div className="error-state">
          <div className="error-icon">❌</div>
          <h3>Processing failed</h3>
          <p>We couldn't process "{lesson.title}". Please try uploading the file again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="lesson-viewer">
      <div className="lesson-header">
        <div className="header-content">
          <h2>{lesson.title}</h2>
          <div className="lesson-progress">
            <span>{microLessons.length} micro-lessons</span>
          </div>
        </div>
        
        <div className="header-actions">
          <div className="view-selector">
            <button
              className={`view-btn ${multimediaView === 'text' ? 'active' : ''}`}
              onClick={() => setMultimediaView('text')}
            >
              📝 Text
            </button>
            <button
              className={`view-btn ${multimediaView === 'audio' ? 'active' : ''}`}
              onClick={() => setMultimediaView('audio')}
              disabled={!audioLesson}
            >
              🎵 Audio
            </button>
            <button
              className={`view-btn ${multimediaView === 'video' ? 'active' : ''}`}
              onClick={() => setMultimediaView('video')}
              disabled={!videoLesson}
            >
              🎥 Video
            </button>
          </div>
          
          <button
            className="generate-multimedia-btn"
            onClick={() => setShowMultimediaGenerator(true)}
          >
            🚀 Generate Multimedia
          </button>
        </div>
      </div>

      {microLessons.length === 0 ? (
        <div className="no-content">
          <p>No micro-lessons available for this lesson yet.</p>
        </div>
      ) : (
        <>
          <div className="micro-lessons-nav">
            {microLessons.map((microLesson, index) => (
              <button
                key={microLesson.micro_lesson_id}
                className={`micro-lesson-tab ${
                  selectedMicroLesson?.micro_lesson_id === microLesson.micro_lesson_id ? 'active' : ''
                }`}
                onClick={() => setSelectedMicroLesson(microLesson)}
              >
                <span className="tab-number">{index + 1}</span>
                <span className="tab-title">{microLesson.title}</span>
              </button>
            ))}
          </div>

          {selectedMicroLesson && (
            <div className="micro-lesson-content">
              <div className="micro-lesson-header">
                <h3>{selectedMicroLesson.title}</h3>
                {selectedMicroLesson.video_duration && (
                  <span className="duration">⏱️ {selectedMicroLesson.video_duration}</span>
                )}
              </div>

              {/* Content based on selected view */}
              {multimediaView === 'text' && (
                <>
                  <div className="micro-lesson-summary">
                    <p>{selectedMicroLesson.summary}</p>
                  </div>

                  {selectedMicroLesson.video_url && (
                    <div className="video-container">
                      <video
                        controls
                        width="100%"
                        poster="/video-placeholder.jpg"
                      >
                        <source src={selectedMicroLesson.video_url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    </div>
                  )}

                  {selectedMicroLesson.audio_url && (
                    <div className="audio-container">
                      <h4>🎧 Audio Version</h4>
                      <audio controls width="100%">
                        <source src={selectedMicroLesson.audio_url} type="audio/mpeg" />
                        Your browser does not support the audio tag.
                      </audio>
                      {selectedMicroLesson.audio_duration && (
                        <span className="audio-duration">Duration: {selectedMicroLesson.audio_duration}</span>
                      )}
                    </div>
                  )}
                </>
              )}

              {multimediaView === 'audio' && audioLesson && (
                <div className="multimedia-content">
                  <MultimediaPlayer
                    audioLesson={audioLesson}
                    onComplete={() => {
                      console.log('Audio lesson completed');
                    }}
                  />
                </div>
              )}

              {multimediaView === 'video' && videoLesson && (
                <div className="multimedia-content">
                  <MultimediaPlayer
                    videoLesson={videoLesson}
                    onComplete={() => {
                      console.log('Video lesson completed');
                    }}
                  />
                </div>
              )}

              {multimediaView === 'audio' && !audioLesson && (
                <div className="multimedia-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">🎵</div>
                    <h4>No Audio Content Available</h4>
                    <p>Generate audio content for this lesson to listen while learning.</p>
                    <button
                      className="generate-btn"
                      onClick={() => setShowMultimediaGenerator(true)}
                    >
                      Generate Audio
                    </button>
                  </div>
                </div>
              )}

              {multimediaView === 'video' && !videoLesson && (
                <div className="multimedia-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">🎥</div>
                    <h4>No Video Content Available</h4>
                    <p>Generate video content for this lesson to watch while learning.</p>
                    <button
                      className="generate-btn"
                      onClick={() => setShowMultimediaGenerator(true)}
                    >
                      Generate Video
                    </button>
                  </div>
                </div>
              )}

              <div className="lesson-actions">
                <button className="action-button quiz-button" onClick={handleQuizStart}>
                  🧠 Take Quiz
                </button>
                <button className="action-button summary-button">
                  📝 View Summary
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Multimedia Generator Modal */}
      {showMultimediaGenerator && selectedMicroLesson && (
        <div className="modal-overlay">
          <div className="modal-content">
            <MultimediaGenerator
              lessonId={selectedMicroLesson.micro_lesson_id}
              lessonTitle={selectedMicroLesson.title}
              onGenerationComplete={handleMultimediaGeneration}
              onClose={() => setShowMultimediaGenerator(false)}
            />
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
};

export default LessonViewer;