import api from './api';
import { Lesson, MicroLesson } from '../types';

class LessonService {
  async getUserLessons(): Promise<Lesson[]> {
    try {
      const response = await api.get('/api/v1/lessons');
      return response.data;
    } catch (error) {
      console.error('Failed to get user lessons:', error);
      return [];
    }
  }

  async uploadLesson(file: File): Promise<Lesson> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/api/v1/lessons/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      throw new Error('Failed to upload lesson');
    }
  }

  async getMicroLessons(lessonId: string): Promise<MicroLesson[]> {
    try {
      const response = await api.get(`/api/v1/lessons/${lessonId}/micro-lessons`);
      return response.data;
    } catch (error) {
      console.error('Failed to get micro lessons:', error);
      return [];
    }
  }

  async getLesson(lessonId: string): Promise<Lesson | null> {
    try {
      const response = await api.get(`/api/v1/lessons/${lessonId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get lesson:', error);
      return null;
    }
  }
}

export const lessonService = new LessonService();