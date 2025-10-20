/**
 * Frontend-Backend Integration Tests
 * 
 * This file contains basic integration tests to verify that the frontend
 * components can successfully communicate with the backend API endpoints.
 */

import { analyticsService } from '../services/analyticsService';
import { quizService } from '../services/quizService';

// Mock fetch for testing
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Frontend-Backend Integration', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Mock localStorage for auth token
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'mock-jwt-token'),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  describe('Analytics Service Integration', () => {
    test('should fetch dashboard data from correct endpoint', async () => {
      const mockDashboard = {
        user_id: 'test-user',
        period: 7,
        progress: { lessons_completed: 5 },
        metrics: { average_score: 85 }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboard
      });

      const result = await analyticsService.getDashboard();

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/analytics/dashboard', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-jwt-token'
        }
      });
      expect(result).toEqual(mockDashboard);
    });

    test('should fetch learning velocity with period parameter', async () => {
      const mockVelocity = {
        user_id: 'test-user',
        period: 30,
        pace: 'steady',
        daily_averages: { lessons: 1.2 }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockVelocity
      });

      const result = await analyticsService.getLearningVelocity(30);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/analytics/velocity?period=30', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-jwt-token'
        }
      });
      expect(result).toEqual(mockVelocity);
    });

    test('should handle analytics API errors gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(analyticsService.getDashboard()).rejects.toThrow('Failed to fetch dashboard data');
    });
  });

  describe('Quiz Service Integration', () => {
    test('should generate quiz with correct parameters', async () => {
      const mockQuiz = {
        quiz_id: 'quiz-123',
        lesson_id: 'lesson-456',
        questions: [
          {
            id: 'q1',
            type: 'multiple_choice',
            question: 'What is React?',
            options: ['Library', 'Framework', 'Language', 'Tool']
          }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockQuiz
      });

      const result = await quizService.generateQuiz('lesson-456', 'medium', 5);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/quiz/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-jwt-token'
        },
        body: JSON.stringify({
          lesson_id: 'lesson-456',
          difficulty: 'medium',
          num_questions: 5
        })
      });
      expect(result).toEqual(mockQuiz);
    });

    test('should submit quiz answers correctly', async () => {
      const mockResults = {
        quiz_id: 'quiz-123',
        overall_score: 85,
        question_results: [],
        feedback: 'Great job!'
      };

      const answers = { 'q1': 'Library', 'q2': 'True' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults
      });

      const result = await quizService.submitQuiz('quiz-123', answers, 300);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/quiz/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-jwt-token'
        },
        body: JSON.stringify({
          quiz_id: 'quiz-123',
          answers: answers,
          time_spent: 300
        })
      });
      expect(result).toEqual(mockResults);
    });

    test('should request hints for quiz questions', async () => {
      const mockHint = {
        hint_text: 'Think about the primary purpose of React',
        hint_type: 'conceptual'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHint
      });

      const result = await quizService.getHint('quiz-123', 'q1', 'Need help', ['Library']);

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/quiz/hint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-jwt-token'
        },
        body: JSON.stringify({
          quiz_id: 'quiz-123',
          question_id: 'q1',
          user_context: 'Need help',
          current_answers: ['Library']
        })
      });
      expect(result).toEqual(mockHint);
    });
  });

  describe('Error Handling', () => {
    test('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(analyticsService.getDashboard()).rejects.toThrow('Network error');
    });

    test('should handle authentication errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      });

      await expect(quizService.generateQuiz('lesson-1', 'easy', 3)).rejects.toThrow('Failed to generate quiz');
    });

    test('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      await expect(analyticsService.getDashboard()).rejects.toThrow('Invalid JSON');
    });
  });

  describe('Authentication Integration', () => {
    test('should include JWT token in all requests', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      await analyticsService.getDashboard();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-jwt-token'
          })
        })
      );
    });

    test('should handle missing authentication token', async () => {
      // Mock localStorage returning null for token
      window.localStorage.getItem = jest.fn(() => null);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      await analyticsService.getDashboard();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer null'
          })
        })
      );
    });
  });
});

/**
 * Manual Integration Test Checklist
 * 
 * To manually verify frontend-backend integration:
 * 
 * 1. Analytics Dashboard:
 *    - Navigate to analytics page
 *    - Verify dashboard loads with real data
 *    - Check progress charts display correctly
 *    - Confirm performance metrics show accurate information
 *    - Test period selector functionality
 * 
 * 2. Quiz Interface:
 *    - Start a quiz from lesson viewer
 *    - Verify questions load from backend
 *    - Test answer submission
 *    - Check hint functionality
 *    - Confirm quiz results display properly
 * 
 * 3. Error Handling:
 *    - Test with network disconnected
 *    - Verify graceful error messages
 *    - Check retry functionality
 *    - Test with invalid authentication
 * 
 * 4. Performance:
 *    - Monitor network requests in DevTools
 *    - Verify reasonable response times
 *    - Check for unnecessary API calls
 *    - Test with slow network conditions
 */