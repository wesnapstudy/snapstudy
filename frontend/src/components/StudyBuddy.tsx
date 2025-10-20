import React from 'react';
import { Lesson, User } from '../types';

interface StudyBuddyProps {
  lesson: Lesson | null;
  user: User;
}

const StudyBuddy: React.FC<StudyBuddyProps> = ({ lesson, user }) => {
  return (
    <div className="study-buddy">
      <h2>AI Study Buddy</h2>
      {lesson ? (
        <div className="chat-interface">
          <p>Ask me anything about "{lesson.title}"</p>
          <div className="chat-messages">
            <div className="message ai-message">
              <p>Hi {user.first_name || 'there'}! I'm here to help you understand this lesson. What would you like to know?</p>
            </div>
          </div>
          <div className="chat-input">
            <input 
              type="text" 
              placeholder="Ask a question about this lesson..."
              disabled
            />
            <button disabled>Send</button>
          </div>
          <p className="coming-soon">Chat functionality coming soon!</p>
        </div>
      ) : (
        <p>Select a lesson to start chatting with your AI study buddy!</p>
      )}
    </div>
  );
};

export default StudyBuddy;