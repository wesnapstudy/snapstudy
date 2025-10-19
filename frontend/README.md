# SnapStudy Frontend

React-based frontend for the SnapStudy learning platform.

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend server running on http://localhost:8000

### Installation & Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```
   
   Or on Windows:
   ```bash
   start.bat
   ```

3. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

## Features

- **Simple Authentication**: Email/password login and registration
- **Lesson Management**: Upload and view learning materials
- **Micro-lessons**: Bite-sized content with video/audio
- **Study Buddy**: AI chat assistant for questions
- **User Settings**: Profile and learning preferences
- **Responsive Design**: Works on desktop and mobile

## Project Structure

```
src/
├── components/          # React components
│   ├── LoginForm.tsx   # Authentication form
│   ├── MainApp.tsx     # Main application layout
│   ├── Header.tsx      # Navigation header
│   ├── LessonLibrary.tsx # Lesson list and upload
│   ├── LessonViewer.tsx  # Content viewer
│   ├── StudyBuddy.tsx    # AI chat interface
│   ├── UserSettings.tsx  # User preferences
│   └── Footer.tsx        # Footer component
├── services/           # API integration
│   ├── api.ts         # Axios configuration
│   ├── authService.ts # Authentication API
│   ├── lessonService.ts # Lesson management API
│   └── chatService.ts   # Chat API
├── types/             # TypeScript definitions
└── App.tsx           # Root component
```

## API Integration

The frontend integrates with the FastAPI backend through:

- **Authentication**: JWT-based auth with localStorage
- **Lessons**: File upload and content management
- **Chat**: Real-time AI assistant communication
- **User Management**: Profile and preferences

## Development

- **Hot Reload**: Changes automatically refresh the browser
- **TypeScript**: Full type safety and IntelliSense
- **CSS Modules**: Component-scoped styling
- **Responsive**: Mobile-first design approach

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `build/` directory ready for deployment.