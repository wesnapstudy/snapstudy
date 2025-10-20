import React from 'react';
import { Lesson, MicroLesson } from '../types';

interface LessonViewerProps {
  lesson: Lesson | null;
  microLessons: MicroLesson[];
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson, microLessons }) => {
  if (!lesson) {
    return (
      <div className="lesson-viewer">
        <div className="no-lesson">
          <h2>Select a lesson to view</h2>
          <p>Choose a lesson from the library to start learning</p>
        </div>
      </div>
    );
  }

  return (
    <div className="lesson-viewer">
      <div className="lesson-header">
        <h2>{lesson.title}</h2>
        <p>Status: {lesson.status}</p>
      </div>
      
      <div className="micro-lessons">
        <h3>Micro Lessons</h3>
        {microLessons.length === 0 ? (
          <p>Processing lesson content... Please wait.</p>
        ) : (
          <div className="micro-lessons-list">
            {microLessons.map((microLesson, index) => (
              <div key={microLesson.micro_lesson_id} className="micro-lesson">
                <h4>{index + 1}. {microLesson.title}</h4>
                <p>{microLesson.summary}</p>
                {microLesson.video_url && (
                  <div className="media-section">
                    <video controls>
                      <source src={microLesson.video_url} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}
                {microLesson.audio_url && (
                  <div className="media-section">
                    <audio controls>
                      <source src={microLesson.audio_url} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonViewer;