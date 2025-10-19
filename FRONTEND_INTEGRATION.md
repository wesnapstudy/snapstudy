# SnapStudy Frontend Integration Guide

This document explains how the React frontend integrates with the existing FastAPI backend.

## Overview

The frontend has been designed to work seamlessly with your existing FastAPI backend while maintaining minimal changes to the backend code. Here's what was added and modified:

## Backend Changes (Minimal)

### 1. Authentication Updates
- **File**: `backend/src/api/routers/auth.py`
- **Changes**: Simplified JWT authentication replacing AWS Cognito
- **Added**: Simple in-memory user store for demo purposes
- **Dependencies**: Added PyJWT to requirements.txt

### 2. CORS Configuration
- **File**: `backend/src/api/main.py` 
- **Existing**: CORS middleware already configured
- **Works with**: Frontend running on localhost:3000

## Frontend Structure

### Core Components
1. **LoginForm**: Simple email/password authentication
2. **MainApp**: Main application layout with three-panel design
3. **LessonLibrary**: File upload and lesson management
4. **LessonViewer**: Content display with micro-lessons
5. **StudyBuddy**: AI chat interface
6. **UserSettings**: Profile and preferences management

### API Integration
- **Base URL**: http://localhost:8000 (configurable via REACT_APP_API_URL)
- **Authentication**: JWT tokens stored in localStorage
- **Endpoints Used**:
  - `POST /api/v1/auth/login` - User authentication
  - `POST /api/v1/auth/register` - User registration
  - `GET /api/v1/auth/me` - Current user info
  - `GET /api/v1/lessons` - User lessons
  - `POST /api/v1/content/upload` - File upload
  - `POST /api/v1/chat/message` - AI chat

## Quick Setup

### 1. Install Frontend Dependencies
```bash
cd study/frontend
npm install
```

### 2. Start Backend Server
```bash
cd study/backend
python start_server.py
```

### 3. Start Frontend Development Server
```bash
cd study/frontend
npm start
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## Key Features Implemented

### ✅ Authentication System
- Simple JWT-based authentication
- User registration and login
- Protected routes and API calls
- Automatic token refresh handling

### ✅ Lesson Management
- File upload with drag-and-drop
- Lesson library with status indicators
- Integration with existing lesson processing

### ✅ Content Viewing
- Micro-lesson navigation
- Video/audio playback
- Progress tracking
- Quiz and summary integration points

### ✅ AI Chat Integration
- Real-time chat with Study Buddy
- Context-aware conversations
- Session management
- Integration with existing chat API

### ✅ User Experience
- Responsive design for all devices
- Loading states and error handling
- Intuitive navigation
- Modern UI with gradients and animations

## Integration Points

### Existing Backend APIs Used
The frontend integrates with your existing API endpoints:

1. **Lessons API** (`/api/v1/lessons`)
2. **Content API** (`/api/v1/content`) 
3. **Chat API** (`/api/v1/chat`)
4. **Analytics API** (`/api/v1/analytics`)
5. **AI Services** (`/api/v1/ai`)

### Data Flow
1. User authenticates → JWT token stored
2. Token included in all API requests
3. Backend processes requests using existing logic
4. Frontend displays results with modern UI

## Customization Options

### Environment Variables
Create `.env` file in frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=SnapStudy
```

### Styling
- CSS files in `src/components/` for component-specific styles
- Global styles in `src/index.css`
- Gradient themes easily customizable

### API Configuration
- Base URL configurable in `src/services/api.ts`
- Timeout and retry logic included
- Automatic error handling

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

### Serve Static Files
The built files can be served by:
1. FastAPI static file serving
2. Nginx/Apache reverse proxy
3. CDN deployment (AWS CloudFront, etc.)

### Environment Configuration
- Set `REACT_APP_API_URL` to production backend URL
- Configure CORS origins in backend for production domain

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS is configured for frontend URL
   - Check `allow_origins` in `main.py`

2. **Authentication Failures**
   - Verify JWT secret key consistency
   - Check token expiration settings

3. **API Connection Issues**
   - Confirm backend is running on port 8000
   - Check `REACT_APP_API_URL` environment variable

### Development Tips

1. **Hot Reload**: Frontend automatically refreshes on code changes
2. **API Debugging**: Use browser DevTools Network tab
3. **State Management**: React hooks for simple state management
4. **Error Boundaries**: Implemented for graceful error handling

## Next Steps

### Recommended Enhancements
1. **Database Integration**: Replace in-memory user store with real database
2. **File Storage**: Integrate with AWS S3 or similar for file uploads
3. **Real-time Updates**: Add WebSocket support for live notifications
4. **Advanced Analytics**: Enhanced user behavior tracking
5. **Mobile App**: React Native version using same API

### Security Considerations
1. **JWT Security**: Use secure secret keys in production
2. **HTTPS**: Enable SSL/TLS for production
3. **Input Validation**: Additional client-side validation
4. **Rate Limiting**: Implement API rate limiting

This integration provides a solid foundation for your SnapStudy application while maintaining the flexibility to enhance and customize as needed.