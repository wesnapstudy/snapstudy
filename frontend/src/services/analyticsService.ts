import api from './api';
import { AnalyticsDashboard, LearningVelocity, EngagementEvent } from '../types';

interface EngagementEventRequest {
  event_type: string;
  event_data: Record<string, any>;
  session_id?: string;
}

class AnalyticsService {
  async trackEngagementEvent(eventType: string, eventData: Record<string, any>, sessionId?: string): Promise<void> {
    try {
      await api.post('/api/v1/analytics/events', {
        event_type: eventType,
        event_data: eventData,
        session_id: sessionId
      });
    } catch (error) {
      console.error('Error tracking engagement event:', error);
      // Don't throw error for analytics tracking to avoid disrupting user experience
    }
  }

  async getDashboard(): Promise<AnalyticsDashboard> {
    try {
      const response = await api.get('/api/v1/analytics/dashboard');
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics dashboard:', error);
      throw error;
    }
  }

  async getLearningVelocity(days: number = 7): Promise<LearningVelocity> {
    try {
      const response = await api.get(`/api/v1/analytics/velocity?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching learning velocity:', error);
      throw error;
    }
  }

  async getStrugglingConcepts(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/struggling-concepts');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching struggling concepts:', error);
      throw error;
    }
  }

  async getRetentionAnalytics(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/retention');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching retention analytics:', error);
      throw error;
    }
  }

  async getProgressSummary(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/progress');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching progress summary:', error);
      throw error;
    }
  }

  async getLearningPatterns(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/patterns');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching learning patterns:', error);
      throw error;
    }
  }

  async getConceptPerformance(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/concept-performance');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching concept performance:', error);
      throw error;
    }
  }

  async getRecommendations(): Promise<any> {
    try {
      const response = await api.get('/api/v1/analytics/recommendations');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      throw error;
    }
  }

  // Convenience methods for common tracking events
  async trackLessonStarted(lessonId: string, sessionId?: string): Promise<void> {
    await this.trackEngagementEvent('lesson_started', { lesson_id: lessonId }, sessionId);
  }

  async trackLessonCompleted(lessonId: string, timeSpent: number, sessionId?: string): Promise<void> {
    await this.trackEngagementEvent('lesson_completed', { 
      lesson_id: lessonId, 
      time_spent: timeSpent 
    }, sessionId);
  }

  async trackQuizCompleted(quizId: string, score: number, timeSpent: number, sessionId?: string): Promise<void> {
    await this.trackEngagementEvent('quiz_completed', { 
      quiz_id: quizId, 
      score, 
      time_spent: timeSpent 
    }, sessionId);
  }

  async trackChatInteraction(sessionId: string, intent: string, timeSpent: number): Promise<void> {
    await this.trackEngagementEvent('chat_interaction', { 
      session_id: sessionId, 
      intent, 
      time_spent: timeSpent 
    });
  }

  async trackContentUploaded(lessonId: string, contentType: string): Promise<void> {
    await this.trackEngagementEvent('content_uploaded', { 
      lesson_id: lessonId, 
      content_type: contentType 
    });
  }
}

export const analyticsService = new AnalyticsService();