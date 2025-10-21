import React, { useState, useEffect, Suspense } from 'react';
import { authService } from './services/authService';
import { User, OnboardingData } from './types';
import ErrorBoundary from './components/ErrorBoundary';
import { performanceMonitor, usePerformanceMonitor } from './utils/performance';
import { RoutePreloader } from './utils/lazyLoading';
import { config } from './config';
import './App.css';

// Lazy load main components
const LoginForm = React.lazy(() => import('./components/LoginForm'));
const OnboardingFlow = React.lazy(() => import('./components/OnboardingFlow'));
const MainApp = React.lazy(() => import('./components/MainApp'));

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
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
        // Skip auth check if API is not properly configured
        if (!config.api.baseUrl || 
            config.api.baseUrl.includes('PLACEHOLDER') || 
            config.api.baseUrl.includes('your-api-domain.com')) {
          console.log('API not configured, skipping authentication');
          setIsAuthenticated(false);
          setUser(null);
          setNeedsOnboarding(false);
          return;
        }

        if (authService.isAuthenticated()) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          setIsAuthenticated(true);
          
          // Check if user needs onboarding
          setNeedsOnboarding(!currentUser.onboarding_completed);
          
          // Track successful authentication
          performanceMonitor.recordMetric('AuthenticationSuccess', 1);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authService.logout();
        setIsAuthenticated(false);
        setUser(null);
        setNeedsOnboarding(false);
        
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
        
        // Check if user needs onboarding
        setNeedsOnboarding(!response.user.onboarding_completed);
        
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
        await authService.register(userData);
        // Track successful registration
        performanceMonitor.recordMetric('RegistrationSuccess', 1);
        
        // Registration successful - user will be prompted to login
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

  const handleOnboardingComplete = async (onboardingData: OnboardingData) => {
    await measureAsyncOperation('onboarding', async () => {
      try {
        const updatedUser = await authService.completeOnboarding(onboardingData);
        setUser(updatedUser);
        setNeedsOnboarding(false);
        
        // Track successful onboarding
        performanceMonitor.recordMetric('OnboardingSuccess', 1);
      } catch (error) {
        console.error('Onboarding failed:', error);
        
        // Track onboarding failure
        performanceMonitor.recordMetric('OnboardingFailure', 1, {
          error: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      }
    });
  };

  const handleOnboardingSkip = () => {
    setNeedsOnboarding(false);
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setNeedsOnboarding(false);
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
        ) : needsOnboarding ? (
          <OnboardingFlow 
            onComplete={handleOnboardingComplete}
            onSkip={handleOnboardingSkip}
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