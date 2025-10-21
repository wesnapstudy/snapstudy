import api from './api';
import { User, OnboardingData } from '../types';
import { config } from '../config';
import { profileService } from './profileService';

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
  private profileUserKey = 'profile_user';

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // First, try to authenticate with profile.json
    const profileUser = await profileService.authenticateWithProfile(
      credentials.email,
      credentials.password
    );

    if (profileUser) {
      // Store profile user flag and user data
      localStorage.setItem(this.profileUserKey, 'true');
      localStorage.setItem('user_data', JSON.stringify(profileUser));
      console.log('Logged in as profile user');
      return { user: profileUser, token: 'profile-token' };
    }

    // If profile authentication fails, try API authentication
    try {
      const response = await api.post('/api/v1/auth/login', credentials);
      const { access_token } = response.data;

      localStorage.setItem(this.tokenKey, access_token);
      localStorage.removeItem(this.profileUserKey);

      // Get user data separately
      const user = await this.getCurrentUser();
      return { user, token: access_token };
    } catch (error) {
      throw new Error('Login failed. Please check your credentials.');
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
    // Check if this is a profile user
    const isProfileUser = localStorage.getItem(this.profileUserKey) === 'true';

    if (isProfileUser) {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        return JSON.parse(userData);
      }
    }

    // Otherwise, get from API
    try {
      const response = await api.get('/api/v1/users/me');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get current user');
    }
  }

  isAuthenticated(): boolean {
    // Check if profile user is logged in
    const isProfileUser = localStorage.getItem(this.profileUserKey) === 'true';
    if (isProfileUser) {
      return !!localStorage.getItem('user_data');
    }

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
    localStorage.removeItem(this.profileUserKey);
    localStorage.removeItem('user_data');
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