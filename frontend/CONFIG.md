# Frontend Configuration Guide

This guide explains how to configure the SnapStudy frontend application.

## Quick Setup

There are two ways to set your API URL:

### Method 1: Edit the Config File (Recommended)

1. Open `frontend/src/config/index.ts`
2. Update the `API_BASE_URL` constant:
   ```typescript
   // Set your API base URL here
   const API_BASE_URL = 'https://your-actual-api-domain.com';
   ```

### Method 2: Use Environment Variable

1. Create or update `.env.production`:
   ```
   REACT_APP_API_URL=https://your-actual-api-domain.com
   ```

## Build and Deploy

After updating the configuration:

1. **Build the application**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to S3**: Upload the contents of the `build/` folder to your S3 bucket.

## Configuration Options

### API Settings
- `baseUrl`: The base URL for your backend API
- `timeout`: Request timeout in milliseconds

### AWS Settings
- `region`: AWS region for Cognito and other services
- `userPoolId`: Cognito User Pool ID
- `userPoolClientId`: Cognito User Pool Client ID

### App Settings
- `name`: Application name
- `version`: Application version
- `environment`: Current environment (development, staging, production)

### Feature Flags
- `enableAnalytics`: Enable/disable analytics tracking
- `enablePerformanceMonitoring`: Enable/disable performance monitoring
- `enableErrorReporting`: Enable/disable error reporting

## Validation

The configuration includes automatic validation that will:
- Check if required settings are present
- Warn about localhost URLs in production
- Log configuration in development mode

## Troubleshooting

### Empty Page Issue
If you see an empty page after deployment, check:
1. API URL is correctly set and accessible
2. No console errors in browser developer tools
3. All required environment variables are set

### API Connection Issues
- Ensure the API URL is correct and accessible
- Check CORS settings on your backend
- Verify SSL certificates for HTTPS URLs

### Authentication Issues
- Verify AWS Cognito settings
- Check if User Pool ID and Client ID are correct
- Ensure the backend is configured to work with Cognito