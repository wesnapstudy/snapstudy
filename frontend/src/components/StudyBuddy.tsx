import React, { useState } from 'react';
import { Lesson, User } from '../types';

interface StudyBuddyProps {
  lesson: Lesson | null;
  user: User;
}

// Paper plane icon for send button
const PaperPlaneIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24">
    <path d="M2 21l20-9L2 3l5 8-5 10zm7-7 11-2-11-2 0 4z" fill="currentColor"/>
  </svg>
);

const StudyBuddy: React.FC<StudyBuddyProps> = ({ lesson, user }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { type: 'ai', text: '👋 Hi! Ask me to summarize, explain, or quiz you on this lesson.' },
    { type: 'user', text: 'Give me a 2-sentence summary.' },
    { type: 'ai', text: 'ANN speeds up similarity search by approximating nearest neighbors. It preserves accuracy with much lower latency.' }
  ]);

  const handleSend = () => {
    if (!message.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { type: 'user', text: message }]);
    setMessage('');
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: 'ai',
        text: `🤖 Here's a concise reply to: ${message}`
      }]);
    }, 500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <>
      <div className="panel-header">Study Buddy</div>
      <div className="panel-body tutor-panel">
        <div className="thread">
          {messages.map((msg, index) => (
            <div key={index} className={`bubble ${msg.type === 'ai' ? 'ai' : 'me'}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="tutor-input">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message…"
            aria-label="Type a message"
          />
        </div>
        <button className="fab-send" title="Send" aria-label="Send" onClick={handleSend}>
          <PaperPlaneIcon />
        </button>
      </div>
    </>
  );
};

export default StudyBuddy;