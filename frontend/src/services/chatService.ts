import api from './api';
import { ChatMessage, ChatResponse } from '../types';

class ChatService {
  async sendMessage(message: string, lessonId?: string, sessionId?: string): Promise<ChatResponse> {
    try {
      const response = await api.post('/api/v1/chat/message', {
        message,
        lesson_id: lessonId,
        session_id: sessionId
      });
      
      return response.data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  }

  async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    try {
      const response = await api.get(`/api/v1/chat/history/${sessionId}`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  }

  async startNewSession(lessonId?: string): Promise<string> {
    try {
      const response = await api.post('/api/v1/chat/session', {
        lesson_id: lessonId
      });
      
      return response.data.session_id;
    } catch (error) {
      console.error('Error starting chat session:', error);
      throw error;
    }
  }
}

export const chatService = new ChatService();