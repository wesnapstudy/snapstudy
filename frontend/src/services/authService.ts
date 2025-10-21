import api from './api';
import { User, OnboardingData } from '../types';
import { config } from '../config';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface AuthResponse {
  user: User;
  token: string;
}

class AuthService {
  private tokenKey = 'auth_token';

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post('/api/v1/auth/login', credentials);
      const { access_token } = response.data;
      
      localStorage.setItem(this.tokenKey, access_token);
      
      // Get user data separately
      const user = await this.getCurrentUser();
      return { user, token: access_token };
    } catch (error) {
      throw new Error('Login failed');
    }
  }

  async register(userData: RegisterData): Promise<void> {
    try {
      await api.post('/api/v1/auth/register', userData);
      // Don't auto-login after registration
    } catch (error) {
      throw new Error('Registration failed');
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get('/api/v1/users/me');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get current user');
    }
  }

  isAuthenticated(): boolean {
    // If API URL is not properly configured, skip authentication
    if (!config.api.baseUrl || 
        config.api.baseUrl.includes('PLACEHOLDER') || 
        config.api.baseUrl.includes('your-api-domain.com')) {
      return false;
    }
    return !!localStorage.getItem(this.tokenKey);
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  async completeOnboarding(onboardingData: OnboardingData): Promise<User> {
    try {
      const response = await api.post('/api/v1/users/onboarding', onboardingData);
      return response.data.user;
    } catch (error) {
      throw new Error('Failed to complete onboarding');
    }
  }

  async updateProfile(profileData: Partial<User>): Promise<User> {
    try {
      const response = await api.put('/api/v1/users/profile', profileData);
      return response.data.user;
    } catch (error) {
      throw new Error('Failed to update profile');
    }
  }
}

export const authService = new AuthService();