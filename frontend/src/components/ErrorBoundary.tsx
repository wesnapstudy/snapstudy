/**
 * Error Boundary component for handling React errors gracefully.
 * 
 * Provides fallback UI and error reporting for production-ready error handling.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report error to monitoring service
    this.reportError(error, errorInfo);
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    try {
      // In a real application, you would send this to your error reporting service
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      };

      // Example: Send to analytics service
      // analyticsService.trackError(errorReport);
      
      console.error('Error Report:', errorReport);
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <div className="error-icon">⚠️</div>
            <h2>Something went wrong</h2>
            <p>We're sorry, but something unexpected happened.</p>
            
            <div className="error-actions">
              <button 
                className="retry-button"
                onClick={this.handleRetry}
              >
                Try Again
              </button>
              <button 
                className="reload-button"
                onClick={this.handleReload}
              >
                Reload Page
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary>Error Details (Development Only)</summary>
                <div className="error-stack">
                  <h4>Error Message:</h4>
                  <pre>{this.state.error.message}</pre>
                  
                  <h4>Stack Trace:</h4>
                  <pre>{this.state.error.stack}</pre>
                  
                  {this.state.errorInfo && (
                    <>
                      <h4>Component Stack:</h4>
                      <pre>{this.state.errorInfo.componentStack}</pre>
                    </>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component for wrapping components with error boundary
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  const WithErrorBoundaryComponent = (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundaryComponent.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithErrorBoundaryComponent;
}

/**
 * Specialized error boundaries for different parts of the app
 */
export const MultimediaErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={
      <div className="multimedia-error">
        <h3>Multimedia Error</h3>
        <p>There was an error loading the multimedia content. Please try refreshing the page.</p>
      </div>
    }
    onError={(error, errorInfo) => {
      console.error('Multimedia component error:', error);
      // Track multimedia-specific errors
    }}
  >
    {children}
  </ErrorBoundary>
);

export const QuizErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={
      <div className="quiz-error">
        <h3>Quiz Error</h3>
        <p>There was an error with the quiz. Your progress has been saved. Please try again.</p>
      </div>
    }
    onError={(error, errorInfo) => {
      console.error('Quiz component error:', error);
      // Track quiz-specific errors
    }}
  >
    {children}
  </ErrorBoundary>
);

export const AnalyticsErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={
      <div className="analytics-error">
        <h3>Analytics Error</h3>
        <p>There was an error loading your analytics. The rest of the app is still working normally.</p>
      </div>
    }
    onError={(error, errorInfo) => {
      console.error('Analytics component error:', error);
      // Track analytics-specific errors
    }}
  >
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;