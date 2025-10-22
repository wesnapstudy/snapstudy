/**
 * SnapStudy Configuration
 * 
 * UPDATE THE API_BASE_URL BELOW TO MATCH YOUR BACKEND
 */

// =============================================================================
// 🔧 CHANGE THIS URL TO MATCH YOUR BACKEND
// =============================================================================
const API_BASE_URL = 'http://localhost:8000';

// Examples:
// const API_BASE_URL = 'http://localhost:8001';
// const API_BASE_URL = 'https://your-api.execute-api.us-east-1.amazonaws.com/prod';
// const API_BASE_URL = 'https://api.yourdomain.com';
// =============================================================================

export const config = {
  api: {
    baseUrl: API_BASE_URL,
    timeout: 15000
  }
};