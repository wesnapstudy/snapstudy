import React, { useState, useEffect, Suspense } from 'react';
import { authService } from './services/authService';
import { User } from './types';
import ErrorBoundary from './components/ErrorBoundary';
import { performanceMonitor, usePerformanceMonitor } from './utils/performance';
import { RoutePreloader } from './utils/lazyLoading';
import './App.css';

// Lazy load main components
const LoginForm = React.lazy(() => import('./components/LoginForm'));
const MainApp = React.lazy(() => import('./components/MainApp'));

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { measureAsyncOperation } = usePerformanceMonitor('App');

  useEffect(() => {
    checkAuthState();
    
    // Preload components after initial load
    setTimeout(() => {
      RoutePreloader.preloadAll();
    }, 2000);
  }, []);

  const checkAuthState = async () => {
    await measureAsyncOperation('checkAuthState', async () => {
      try {
        if (authService.isAuthenticated()) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          setIsAuthenticated(true);
          
          // Track successful authentication
          performanceMonitor.recordMetric('AuthenticationSuccess', 1);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authService.logout();
        setIsAuthenticated(false);
        setUser(null);
        
        // Track authentication failure
        performanceMonitor.recordMetric('AuthenticationFailure', 1, {
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      } finally {
        setLoading(false);
      }
    });
  };

  const handleLogin = async (email: string, password: string) => {
    await measureAsyncOperation('login', async () => {
      try {
        const response = await authService.login({ email, password });
        setUser(response.user);
        setIsAuthenticated(true);
        
        // Track successful login
        performanceMonitor.recordMetric('LoginSuccess', 1);
      } catch (error) {
        console.error('Login failed:', error);
        
        // Track login failure
        performanceMonitor.recordMetric('LoginFailure', 1, {
          error: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      }
    });
  };

  const handleRegister = async (userData: any) => {
    await measureAsyncOperation('register', async () => {
      try {
        const response = await authService.register(userData);
        setUser(response.user);
        setIsAuthenticated(true);
        
        // Track successful registration
        performanceMonitor.recordMetric('RegistrationSuccess', 1);
      } catch (error) {
        console.error('Registration failed:', error);
        
        // Track registration failure
        performanceMonitor.recordMetric('RegistrationFailure', 1, {
          error: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      }
    });
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading SnapStudy...</p>
      </div>
    );
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Track application errors
        performanceMonitor.recordMetric('ApplicationError', 1, {
          error: error.message,
          componentStack: errorInfo.componentStack
        });
      }}
    >
      <Suspense fallback={
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading application...</p>
        </div>
      }>
        {!isAuthenticated || !user ? (
          <LoginForm 
            onLogin={handleLogin}
            onRegister={handleRegister}
          />
        ) : (
          <MainApp 
            user={user}
            onLogout={handleLogout}
          />
        )}
      </Suspense>
    </ErrorBoundary>
  );
};

export default App;