import React, { useState, useEffect, useRef } from 'react';
import { Lesson, User, ChatMessage } from '../types';
import { chatService } from '../services/chatService';
import './StudyBuddy.css';

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
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session and load history
  useEffect(() => {
    const initializeChat = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Start new session
        const newSessionId = await chatService.startNewSession(lesson?.lesson_id);
        setSessionId(newSessionId);
        
        // Load chat history
        const history = await chatService.getChatHistory(newSessionId);
        setMessages(history);
        
        // Add welcome message if no history
        if (history.length === 0) {
          const welcomeMessage: ChatMessage = {
            id: 'welcome',
            content: '👋 Hi! Ask me to summarize, explain, or quiz you on this lesson.',
            sender: 'ai',
            timestamp: new Date()
          };
          setMessages([welcomeMessage]);
        }
      } catch (err) {
        console.error('Failed to initialize chat:', err);
        setError('Failed to connect to chat service. Please try again.');
        
        // Fallback to welcome message
        const welcomeMessage: ChatMessage = {
          id: 'welcome',
          content: '👋 Hi! Ask me to summarize, explain, or quiz you on this lesson.',
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, [lesson?.lesson_id]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cleanup WebSocket connection on unmount
  useEffect(() => {
    return () => {
      chatService.disconnect();
    };
  }, []);

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;
    
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: message.trim(),
      sender: 'user',
      timestamp: new Date()
    };
    
    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const messageContent = message.trim();
    setMessage('');
    setIsLoading(true);
    setError(null);
    
    // Create placeholder for streaming AI response
    const aiMessageId = `ai-${Date.now()}`;
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      content: '',
      sender: 'ai',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, aiMessage]);
    
    try {
      // Try WebSocket streaming first if available
      if (chatService.isWebSocketConnected() || sessionId) {
        let streamingContent = '';
        
        await chatService.sendStreamingMessage(
          messageContent,
          lesson?.lesson_id,
          sessionId || undefined,
          {
            onChunk: (chunk: string) => {
              streamingContent += chunk;
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === aiMessageId 
                    ? { ...msg, content: streamingContent }
                    : msg
                )
              );
            },
            onComplete: (fullMessage: string) => {
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === aiMessageId 
                    ? { ...msg, content: fullMessage }
                    : msg
                )
              );
              setIsLoading(false);
            },
            onError: (error: string) => {
              console.error('Streaming error:', error);
              // Fallback to regular API call
              fallbackToRegularAPI();
            }
          }
        );
      } else {
        // Fallback to regular API call
        await fallbackToRegularAPI();
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      await fallbackToRegularAPI();
    }
    
    async function fallbackToRegularAPI() {
      try {
        const response = await chatService.sendMessage(
          messageContent,
          lesson?.lesson_id,
          sessionId || undefined
        );
        
        // Update AI message with response
        setMessages(prev => 
          prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: response.content }
              : msg
          )
        );
        
        // Update session ID if provided
        if (response.session_id) {
          setSessionId(response.session_id);
        }
      } catch (fallbackErr) {
        console.error('Fallback API call failed:', fallbackErr);
        setError('Failed to send message. Please try again.');
        
        // Update AI message with error
        setMessages(prev => 
          prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: '❌ Sorry, I encountered an error. Please try again.' }
              : msg
          )
        );
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <div className="panel-header">Study Buddy</div>
      <div className="panel-body tutor-panel">
        {error && (
          <div className="error-message" style={{ 
            color: '#e74c3c', 
            padding: '8px', 
            marginBottom: '8px', 
            fontSize: '14px',
            backgroundColor: '#fdf2f2',
            border: '1px solid #fecaca',
            borderRadius: '4px'
          }}>
            {error}
          </div>
        )}
        
        <div className="thread">
          {messages.map((msg) => (
            <div key={msg.id} className={`bubble ${msg.sender === 'ai' ? 'ai' : 'me'}`}>
              {msg.content}
            </div>
          ))}
          
          {isLoading && (
            <div className="bubble ai">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="tutor-input">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? "AI is thinking..." : "Type a message…"}
            aria-label="Type a message"
            disabled={isLoading}
          />
        </div>
        
        <button 
          className="fab-send" 
          title="Send" 
          aria-label="Send" 
          onClick={handleSend}
          disabled={isLoading || !message.trim()}
          style={{ 
            opacity: isLoading || !message.trim() ? 0.5 : 1,
            cursor: isLoading || !message.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          <PaperPlaneIcon />
        </button>
      </div>
    </>
  );
};

export default StudyBuddy;