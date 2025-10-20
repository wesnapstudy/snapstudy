import React from 'react';
import { Lesson } from '../types';

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
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onLessonUpload(file);
    }
  };

  return (
    <div className="lesson-library">
      <h2>Your Lessons</h2>
      
      <div className="upload-section">
        <input
          type="file"
          id="file-upload"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-upload" className="upload-button">
          Upload New Lesson
        </label>
      </div>
      
      <div className="lessons-list">
        {lessons.length === 0 ? (
          <p>No lessons yet. Upload your first lesson to get started!</p>
        ) : (
          lessons.map((lesson) => (
            <div
              key={lesson.lesson_id}
              className={`lesson-item ${selectedLesson?.lesson_id === lesson.lesson_id ? 'selected' : ''}`}
              onClick={() => onLessonSelect(lesson)}
            >
              <h3>{lesson.title}</h3>
              <p>Status: {lesson.status}</p>
              <p>Created: {new Date(lesson.created_at).toLocaleDateString()}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LessonLibrary;