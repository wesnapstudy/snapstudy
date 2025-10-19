import api from './api';
import { Lesson, MicroLesson } from '../types';

class LessonService {
  async getUserLessons(): Promise<Lesson[]> {
    try {
      const response = await api.get('/api/v1/lessons');
      return response.data.lessons || [];
    } catch (error) {
      console.error('Error fetching user lessons:', error);
      return [];
    }
  }

  async getMicroLessons(lessonId: string): Promise<MicroLesson[]> {
    try {
      const response = await api.get(`/api/v1/lessons/${lessonId}/micro-lessons`);
      return response.data.microLessons || [];
    } catch (error) {
      console.error('Error fetching micro lessons:', error);
      return [];
    }
  }

  async uploadLesson(file: File): Promise<Lesson> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/v1/content/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data.lesson;
    } catch (error) {
      console.error('Error uploading lesson:', error);
      throw error;
    }
  }

  async deleteLesson(lessonId: string): Promise<void> {
    try {
      await api.delete(`/api/v1/lessons/${lessonId}`);
    } catch (error) {
      console.error('Error deleting lesson:', error);
      throw error;
    }
  }

  async getLessonProgress(lessonId: string): Promise<any> {
    try {
      const response = await api.get(`/api/v1/adaptive/progress/${lessonId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching lesson progress:', error);
      return null;
    }
  }
}

export const lessonService = new LessonService();