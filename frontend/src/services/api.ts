import axios, { AxiosResponse, AxiosError } from 'axios';
import { config } from '../config';
import { SecurityValidator, CertificateValidator } from '../utils/security';

// Enforce HTTPS for API base URL
const secureBaseUrl = SecurityValidator.enforceHttps(config.api.baseUrl);

// Validate HTTPS usage
if (!SecurityValidator.validateHttpsUrl(secureBaseUrl) && !secureBaseUrl.includes('localhost')) {
  console.error('API must use HTTPS in production environment');
}

// Create axios instance with security headers
const api = axios.create({
  baseURL: secureBaseUrl,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // CSRF protection
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
  },
});

// Add auth token and security validation to requests
api.interceptors.request.use(async (config) => {
  // Add auth token (import authService to avoid circular dependency)
  const token = localStorage.getItem('auth_token'); // Fallback to localStorage for now
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Sanitize request data
  if (config.data) {
    config.data = SecurityValidator.sanitizeRequestData(config.data);
  }

  // Sanitize URL parameters
  if (config.params) {
    config.params = SecurityValidator.sanitizeRequestData(config.params);
  }

  // Ensure HTTPS for the request URL
  if (config.url && !config.url.startsWith('/')) {
    config.url = SecurityValidator.enforceHttps(config.url);
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

// Handle auth errors and security validation
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Validate security headers
    const headers: Record<string, string> = {};
    Object.entries(response.headers).forEach(([key, value]) => {
      if (typeof value === 'string') {
        headers[key] = value;
      }
    });
    const headerValidation = SecurityValidator.validateSecurityHeaders(headers);
    if (!headerValidation.valid && process.env.NODE_ENV === 'development') {
      console.warn('Missing security headers:', headerValidation.missing);
      if (headerValidation.warnings.length > 0) {
        console.warn('Security header warnings:', headerValidation.warnings);
      }
    }

    // Validate response data for security issues
    if (response.data) {
      const dataValidation = SecurityValidator.validateResponseData(response.data);
      if (!dataValidation.safe) {
        console.error('Security issues in response data:', dataValidation.issues);
        // In production, you might want to reject the response
        if (process.env.NODE_ENV === 'production') {
          return Promise.reject(new Error('Response data failed security validation'));
        }
      }
    }

    return response;
  },
  (error: AxiosError) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }

    // Log security-related errors
    if (error.response?.status === 403) {
      console.warn('Access forbidden - possible security issue');
    }

    // Handle SSL/TLS errors
    if (error.code === 'CERT_INVALID' || error.message?.includes('certificate')) {
      console.error('SSL Certificate validation failed');
    }

    return Promise.reject(error);
  }
);

export default api;

// Security validation functions for external use
export const validateApiSecurity = async (): Promise<{
  httpsEnforced: boolean;
  certificateValid: boolean;
  secureContext: boolean;
}> => {
  const httpsEnforced = SecurityValidator.validateHttpsUrl(secureBaseUrl);
  const certificateValidation = await CertificateValidator.validateCertificate(secureBaseUrl);
  const secureContext = CertificateValidator.isSecureContext();

  return {
    httpsEnforced,
    certificateValid: certificateValidation.valid,
    secureContext
  };
};

// Export security utilities for use in other services
export { SecurityValidator, CertificateValidator };