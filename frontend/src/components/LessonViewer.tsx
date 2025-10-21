import React from 'react';
import { Lesson, MicroLesson } from '../types';

interface LessonViewerProps {
  lesson: Lesson | null;
  microLessons: MicroLesson[];
}

// SVG Icons matching snapstudy.html
const PlayIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24">
    <path d="M8 5v14l11-7z" fill="currentColor"/>
  </svg>
);

const AudioIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24">
    <path d="M14 3.23v17.54c0 .79-.9 1.27-1.54.82L7 18H4a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1h3l5.46-3.59c.64-.45 1.54.03 1.54.82z" fill="currentColor"/>
  </svg>
);

const QuizIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24">
    <path d="M20 2H8a2 2 0 0 0-2 2v3H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3h2a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Zm-4 18H4V9h12Zm4-5h-2V9a2 2 0 0 0-2-2H8V4h12Z" fill="currentColor"/>
  </svg>
);

const SummaryIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24">
    <path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5L14 3.5ZM8 11h8v2H8v-2Zm0 4h8v2H8v-2Z" fill="currentColor"/>
  </svg>
);

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson, microLessons }) => {
  return (
    <>
      <div className="panel-header">My Snaps</div>
      <div className="panel-body">
        {!lesson || microLessons.length === 0 ? (
          <>
            {/* Default content matching snapstudy.html */}
            <div className="card">
              <h3>Recap</h3>
              <p>Cosine similarity measures how close two vectors are in direction—great for comparing text embeddings.</p>
              <div className="actions">
                <button className="icon-btn">
                  <span className="ico"><PlayIcon /></span>
                  <span>Video</span>
                  <span className="meta">2:45</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><AudioIcon /></span>
                  <span>Audio</span>
                  <span className="meta">1:10</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><QuizIcon /></span>
                  <span>Quiz</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><SummaryIcon /></span>
                  <span>Summary</span>
                </button>
              </div>
            </div>

            <div className="card">
              <h3>Approximate Nearest Neighbor (ANN)</h3>
              <p>ANN indexes (HNSW, IVF-Flat) trade exactness for speed, enabling scalable similarity search with low latency.</p>
              <div className="actions">
                <button className="icon-btn">
                  <span className="ico"><PlayIcon /></span>
                  <span>Video</span>
                  <span className="meta">3:30</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><AudioIcon /></span>
                  <span>Audio</span>
                  <span className="meta">1:25</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><QuizIcon /></span>
                  <span>Quiz</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><SummaryIcon /></span>
                  <span>Summary</span>
                </button>
              </div>
            </div>
          </>
        ) : (
          microLessons.map((microLesson, index) => (
            <div key={microLesson.micro_lesson_id} className="card">
              <h3>{microLesson.title}</h3>
              <p>{microLesson.summary}</p>
              <div className="actions">
                {microLesson.video_url && (
                  <button className="icon-btn">
                    <span className="ico"><PlayIcon /></span>
                    <span>Video</span>
                  </button>
                )}
                {microLesson.audio_url && (
                  <button className="icon-btn">
                    <span className="ico"><AudioIcon /></span>
                    <span>Audio</span>
                  </button>
                )}
                <button className="icon-btn">
                  <span className="ico"><QuizIcon /></span>
                  <span>Quiz</span>
                </button>
                <button className="icon-btn">
                  <span className="ico"><SummaryIcon /></span>
                  <span>Summary</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </>
  );
};

export default LessonViewer;