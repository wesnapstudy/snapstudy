/**
 * Error Boundary component for handling React errors gracefully.
 * 
 * Provides fallback UI and error reporting for production-ready error handling.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import './ErrorBoundary.css';
import { analyticsService } from '../services/analyticsService';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  enableGracefulDegradation?: boolean;
  criticalFeature?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  userFeedback: string;
  showFeedbackForm: boolean;
  isReporting: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      userFeedback: '',
      showFeedbackForm: false,
      isReporting: false
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
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

  private reportError = async (error: Error, errorInfo: ErrorInfo, userFeedback?: string) => {
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        userFeedback: userFeedback || '',
        criticalFeature: this.props.criticalFeature || false,
        gracefulDegradation: this.props.enableGracefulDegradation || false
      };

      // Report to analytics service
      await analyticsService.trackEngagementEvent('error_boundary_triggered', errorReport);
      
      console.error('Error Report:', errorReport);
      
      // Store error locally for debugging
      const storedErrors = JSON.parse(localStorage.getItem('error_reports') || '[]');
      storedErrors.push(errorReport);
      
      // Keep only last 10 errors
      if (storedErrors.length > 10) {
        storedErrors.splice(0, storedErrors.length - 10);
      }
      
      localStorage.setItem('error_reports', JSON.stringify(storedErrors));
      
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      userFeedback: '',
      showFeedbackForm: false,
      isReporting: false
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleShowFeedback = () => {
    this.setState({ showFeedbackForm: true });
  };

  private handleFeedbackChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    this.setState({ userFeedback: event.target.value });
  };

  private handleSubmitFeedback = async () => {
    if (this.state.error && this.state.errorInfo) {
      this.setState({ isReporting: true });
      await this.reportError(this.state.error, this.state.errorInfo, this.state.userFeedback);
      this.setState({ 
        isReporting: false, 
        showFeedbackForm: false,
        userFeedback: ''
      });
    }
  };

  private handleGracefulDegradation = () => {
    // For non-critical features, try to continue with limited functionality
    if (this.props.enableGracefulDegradation && !this.props.criticalFeature) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null
      });
    }
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
              {this.props.enableGracefulDegradation && !this.props.criticalFeature && (
                <button 
                  className="continue-button"
                  onClick={this.handleGracefulDegradation}
                >
                  Continue Anyway
                </button>
              )}
            </div>

            <div className="error-feedback">
              {!this.state.showFeedbackForm ? (
                <button 
                  className="feedback-button"
                  onClick={this.handleShowFeedback}
                >
                  Report Issue
                </button>
              ) : (
                <div className="feedback-form">
                  <h4>Help us improve</h4>
                  <p>What were you trying to do when this error occurred?</p>
                  <textarea
                    className="feedback-textarea"
                    value={this.state.userFeedback}
                    onChange={this.handleFeedbackChange}
                    placeholder="Describe what happened..."
                    rows={3}
                  />
                  <div className="feedback-actions">
                    <button 
                      className="submit-feedback-button"
                      onClick={this.handleSubmitFeedback}
                      disabled={this.state.isReporting}
                    >
                      {this.state.isReporting ? 'Sending...' : 'Send Report'}
                    </button>
                    <button 
                      className="cancel-feedback-button"
                      onClick={() => this.setState({ showFeedbackForm: false, userFeedback: '' })}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
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