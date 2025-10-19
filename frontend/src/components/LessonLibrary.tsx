import React, { useState } from 'react';
import { Lesson } from '../types';
import UploadModal from './UploadModal';
import './LessonLibrary.css';

interface LessonLibraryProps {
  lessons: Lesson[];
  selectedLesson: Lesson | null;
  onLessonSelect: (lesson: Lesson) => void;
  onLessonUpload: (file: File) => void;
}

const LessonLibrary: React.FC<LessonLibraryProps> = ({
  lessons,
  selectedLesson,
  onLessonSelect,
  onLessonUpload
}) => {
  const [showUploadModal, setShowUploadModal] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      default: return '📄';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="lesson-library">
      <div className="library-header">
        <h2>📚 My Lessons</h2>
        <button 
          className="upload-button"
          onClick={() => setShowUploadModal(true)}
        >
          + Upload
        </button>
      </div>

      <div className="lessons-list">
        {lessons.length === 0 ? (
          <div className="empty-state">
            <p>No lessons yet</p>
            <p className="empty-subtitle">Upload your first document to get started!</p>
          </div>
        ) : (
          lessons.map((lesson) => (
            <div
              key={lesson.lesson_id}
              className={`lesson-item ${selectedLesson?.lesson_id === lesson.lesson_id ? 'selected' : ''}`}
              onClick={() => onLessonSelect(lesson)}
            >
              <div className="lesson-icon">
                {getStatusIcon(lesson.status)}
              </div>
              <div className="lesson-info">
                <h3 className="lesson-title">{lesson.title}</h3>
                <p className="lesson-meta">
                  {formatDate(lesson.created_at)} • {lesson.content_type.split('/')[1]?.toUpperCase()}
                </p>
                <div className={`lesson-status ${lesson.status}`}>
                  {lesson.status}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showUploadModal && (
        <UploadModal
          onUpload={onLessonUpload}
          onClose={() => setShowUploadModal(false)}
        />
      )}
    </div>
  );
};

export default LessonLibrary;