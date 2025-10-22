import api from './api';
import { User, OnboardingData } from '../types';
import { config } from '../config';
import { profileService } from './profileService';
import { SecureStorage, SessionManager } from '../utils/secureStorage';

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
  private refreshTokenKey = 'refresh_token';
  private profileUserKey = 'profile_user';
  private userDataKey = 'user_data';

  constructor() {
    // Set up session timeout handler
    SessionManager.onTimeout(() => {
      this.handleSessionTimeout();
    });
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // First, try to authenticate with profile.json
    const profileUser = await profileService.authenticateWithProfile(
      credentials.email,
      credentials.password
    );

    if (profileUser) {
      // Store profile user flag and user data securely
      await SecureStorage.setItem(this.profileUserKey, true, { encrypt: true });
      await SecureStorage.setItem(this.userDataKey, profileUser, { 
        encrypt: true, 
        expirationMinutes: 480 // 8 hours
      });
      
      // Start session management
      SessionManager.startSession(480); // 8 hours
      
      console.log('Logged in as profile user');
      return { user: profileUser, token: 'profile-token' };
    }

    // If profile authentication fails, try API authentication
    try {
      const response = await api.post('/api/v1/auth/login', credentials);
      const { access_token, refresh_token } = response.data;

      // Store tokens securely with encryption
      await SecureStorage.setItem(this.tokenKey, access_token, { 
        encrypt: true, 
        expirationMinutes: 60 // 1 hour for access token
      });
      
      if (refresh_token) {
        await SecureStorage.setItem(this.refreshTokenKey, refresh_token, { 
          encrypt: true, 
          expirationMinutes: 10080 // 7 days for refresh token
        });
      }

      // Clear profile user flag
      await SecureStorage.removeItem(this.profileUserKey);

      // Get user data separately and store securely
      const user = await this.getCurrentUser();
      await SecureStorage.setItem(this.userDataKey, user, { 
        encrypt: true, 
        expirationMinutes: 480 // 8 hours
      });

      // Start session management
      SessionManager.startSession(60); // 1 hour for API sessions

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
    const isProfileUser = await SecureStorage.getItem(this.profileUserKey);

    if (isProfileUser) {
      const userData = await SecureStorage.getItem(this.userDataKey);
      if (userData) {
        return userData;
      }
    }

    // Otherwise, get from API
    try {
      const response = await api.get('/api/v1/users/me');
      // Cache user data securely
      await SecureStorage.setItem(this.userDataKey, response.data, { 
        encrypt: true, 
        expirationMinutes: 480 
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to get current user');
    }
  }

  async isAuthenticated(): Promise<boolean> {
    // Check session validity first
    const sessionValid = await SessionManager.isSessionValid();
    if (!sessionValid) {
      await this.logout();
      return false;
    }

    // Check if profile user is logged in
    const isProfileUser = await SecureStorage.getItem(this.profileUserKey);
    if (isProfileUser) {
      const userData = await SecureStorage.getItem(this.userDataKey);
      return !!userData;
    }

    // If API URL is not properly configured, skip authentication
    if (!config.api.baseUrl ||
        config.api.baseUrl.includes('PLACEHOLDER') ||
        config.api.baseUrl.includes('your-api-domain.com')) {
      return false;
    }

    const token = await SecureStorage.getItem(this.tokenKey);
    return !!token;
  }

  async logout(): Promise<void> {
    // Clear all secure storage
    await SecureStorage.removeItem(this.tokenKey);
    await SecureStorage.removeItem(this.refreshTokenKey);
    await SecureStorage.removeItem(this.profileUserKey);
    await SecureStorage.removeItem(this.userDataKey);
    
    // Clear session
    SessionManager.clearSession();

    // Clear any legacy localStorage items
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('profile_user');
    localStorage.removeItem('user_data');
  }

  async getToken(): Promise<string | null> {
    return await SecureStorage.getItem(this.tokenKey);
  }

  async getRefreshToken(): Promise<string | null> {
    return await SecureStorage.getItem(this.refreshTokenKey);
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
  /
**
   * Handles session timeout
   */
  private async handleSessionTimeout(): Promise<void> {
    console.warn('Session timeout - logging out user');
    await this.logout();
    
    // Show user-friendly notification
    if (window.confirm('Your session has expired for security reasons. Would you like to log in again?')) {
      window.location.href = '/login';
    } else {
      window.location.href = '/';
    }
  }

  /**
   * Refreshes the authentication token
   */
  async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = await this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Store new tokens securely
      await SecureStorage.setItem(this.tokenKey, access_token, { 
        encrypt: true, 
        expirationMinutes: 60 
      });

      if (newRefreshToken) {
        await SecureStorage.setItem(this.refreshTokenKey, newRefreshToken, { 
          encrypt: true, 
          expirationMinutes: 10080 
        });
      }

      // Extend session
      SessionManager.extendSession(60);

      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      await this.logout();
      return null;
    }
  }

  /**
   * Gets remaining session time
   */
  async getSessionTimeRemaining(): Promise<number> {
    return await SessionManager.getRemainingTime();
  }

  /**
   * Extends the current session
   */
  extendSession(): void {
    SessionManager.extendSession();
  }
}