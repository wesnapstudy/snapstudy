import React, { useState } from 'react';
import { Lesson, MicroLesson } from '../types';
import './LessonViewer.css';

interface LessonViewerProps {
  lesson: Lesson | null;
  microLessons: MicroLesson[];
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson, microLessons }) => {
  const [selectedMicroLesson, setSelectedMicroLesson] = useState<MicroLesson | null>(
    microLessons.length > 0 ? microLessons[0] : null
  );

  React.useEffect(() => {
    if (microLessons.length > 0) {
      setSelectedMicroLesson(microLessons[0]);
    }
  }, [microLessons]);

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
        <h2>{lesson.title}</h2>
        <div className="lesson-progress">
          <span>{microLessons.length} micro-lessons</span>
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

              <div className="lesson-actions">
                <button className="action-button quiz-button">
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
    </div>
  );
};

export default LessonViewer;