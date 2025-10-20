import React from 'react';
import { User, UserProfile } from '../types';

interface HeaderProps {
  user: User;
  userProfile: UserProfile | null;
  currentView: string;
  onViewChange: (view: 'lessons' | 'multimedia' | 'settings') => void;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  user, 
  userProfile, 
  currentView, 
  onViewChange, 
  onLogout 
}) => {
  return (
    <header className="app-header">
      <div className="header-left">
        <h1>SnapStudy</h1>
        <nav>
          <button 
            className={currentView === 'lessons' ? 'active' : ''}
            onClick={() => onViewChange('lessons')}
          >
            Lessons
          </button>
          <button 
            className={currentView === 'multimedia' ? 'active' : ''}
            onClick={() => onViewChange('multimedia')}
          >
            Multimedia
          </button>
          <button 
            className={currentView === 'settings' ? 'active' : ''}
            onClick={() => onViewChange('settings')}
          >
            Settings
          </button>
        </nav>
      </div>
      
      <div className="header-right">
        <span>Welcome, {user.first_name || user.email}</span>
        <button onClick={onLogout}>Logout</button>
      </div>
    </header>
  );
};

export default Header;