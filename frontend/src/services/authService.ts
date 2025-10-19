import api from './api';
import { User } from '../types';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/api/v1/auth/login', credentials);
    const { access_token, user } = response.data;
    
    localStorage.setItem('auth_token', access_token);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/api/v1/auth/register', userData);
    const { access_token, user } = response.data;
    
    localStorage.setItem('auth_token', access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  }

  logout(): void {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}

export const authService = new AuthService();