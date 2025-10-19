export interface User {
  id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

export interface Lesson {
  lesson_id: string;
  user_id: string;
  title: string;
  content_type: string;
  s3_key: string;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface MicroLesson {
  micro_lesson_id: string;
  lesson_id: string;
  title: string;
  summary: string;
  sequence_number: number;
  video_url?: string;
  audio_url?: string;
  video_duration?: string;
  audio_duration?: string;
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
}

export interface Quiz {
  quiz_id: string;
  micro_lesson_id: string;
  questions: QuizQuestion[];
  created_at: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export interface ChatResponse {
  content: string;
  session_id?: string;
}

export interface UserProfile {
  user_id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  profile_picture?: string;
  created_at: string;
  updated_at: string;
  last_login: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  notifications_enabled: boolean;
  auto_play_videos: boolean;
  playback_speed: number;
}