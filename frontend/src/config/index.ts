/**
 * Frontend Configuration
 * 
 * Simple configuration file for the SnapStudy frontend.
 * Update the API_BASE_URL below or set REACT_APP_API_URL environment variable.
 */

// =============================================================================
// MAIN CONFIGURATION - UPDATE THIS SECTION
// =============================================================================

// Set your API base URL here
const API_BASE_URL = 'https://your-api-domain.com';

// AWS Configuration (optional - for Cognito authentication)
const AWS_REGION = 'us-east-1';
const USER_POOL_ID = '';
const USER_POOL_CLIENT_ID = '';

// =============================================================================

export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
  };
  aws: {
    region: string;
    userPoolId: string;
    userPoolClientId: string;
  };
  app: {
    name: string;
    version: string;
  };
  features: {
    enableAnalytics: boolean;
    enablePerformanceMonitoring: boolean;
    enableErrorReporting: boolean;
  };
}

// Create configuration object
const createConfig = (): AppConfig => {
  // Use environment variable if provided, otherwise use the constant above
  const apiBaseUrl = process.env.REACT_APP_API_URL || API_BASE_URL;
  
  return {
    api: {
      baseUrl: apiBaseUrl,
      timeout: 15000, // 15 seconds
    },
    aws: {
      region: process.env.REACT_APP_AWS_REGION || AWS_REGION,
      userPoolId: process.env.REACT_APP_USER_POOL_ID || USER_POOL_ID,
      userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || USER_POOL_CLIENT_ID,
    },
    app: {
      name: 'SnapStudy',
      version: '1.0.0',
    },
    features: {
      enableAnalytics: true,
      enablePerformanceMonitoring: true,
      enableErrorReporting: true,
    },
  };
};

// Export the configuration
export const config = createConfig();

// Helper functions
export const isApiConfigured = (): boolean => {
  return !config.api.baseUrl.includes('your-api-domain.com') && 
         !config.api.baseUrl.includes('PLACEHOLDER') &&
         !config.api.baseUrl.includes('localhost');
};

// API helpers
export const getApiUrl = (endpoint: string) => {
  const baseUrl = config.api.baseUrl.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${cleanEndpoint}`;
};

// Validation helper
export const validateConfig = (): boolean => {
  if (!config.api.baseUrl) {
    console.error('API base URL is required');
    return false;
  }
  
  if (!isApiConfigured()) {
    console.warn('API URL not configured. Please update the API_BASE_URL in src/config/index.ts or set REACT_APP_API_URL environment variable.');
  }
  
  return true;
};

// Log configuration on startup (only in development)
if (process.env.NODE_ENV === 'development') {
  console.log('App Configuration:', config);
}

// Validate configuration
validateConfig();