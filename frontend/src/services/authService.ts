import api from './api';
import { User } from '../types';

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
      const { user, token } = response.data;
      
      localStorage.setItem(this.tokenKey, token);
      return { user, token };
    } catch (error) {
      throw new Error('Login failed');
    }
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      const response = await api.post('/api/v1/auth/register', userData);
      const { user, token } = response.data;
      
      localStorage.setItem(this.tokenKey, token);
      return { user, token };
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
    return !!localStorage.getItem(this.tokenKey);
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}

export const authService = new AuthService();