import React, { useState, useRef, useEffect } from 'react';
import { Lesson, User, ChatMessage } from '../types';
import { chatService } from '../services/chatService';
import './StudyBuddy.css';

interface StudyBuddyProps {
  lesson: Lesson | null;
  user: User;
}

const StudyBuddy: React.FC<StudyBuddyProps> = ({ lesson, user }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (lesson) {
      initializeChat();
    }
  }, [lesson]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    try {
      const newSessionId = await chatService.startNewSession(lesson?.lesson_id);
      setSessionId(newSessionId);
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        content: `Hi! I'm your Study Buddy. I'm here to help you understand "${lesson?.title}". Feel free to ask me any questions about the content!`,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(
        inputMessage,
        lesson?.lesson_id,
        sessionId || undefined
      );

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="study-buddy">
      <div className="buddy-header">
        <div className="buddy-avatar">🤖</div>
        <div className="buddy-info">
          <h3>Study Buddy</h3>
          <p>AI Learning Assistant</p>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}
            >
              <div className="message-content">
                {message.content}
              </div>
              <div className="message-time">
                {formatTime(message.timestamp)}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message ai-message">
              <div className="message-content typing">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={lesson ? "Ask me anything about this lesson..." : "Select a lesson to start chatting"}
              disabled={!lesson || isLoading}
              rows={1}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || !lesson || isLoading}
              className="send-button"
            >
              📤
            </button>
          </div>
        </div>
      </div>

      {!lesson && (
        <div className="no-lesson-state">
          <p>Select a lesson to start chatting with your Study Buddy!</p>
        </div>
      )}
    </div>
  );
};

export default StudyBuddy;