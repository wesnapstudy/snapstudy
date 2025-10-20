import React from 'react';
import { User, UserProfile } from '../types';
import './Header.css';

interface HeaderProps {
  user: User;
  userProfile: UserProfile | null;
  currentView: 'lessons' | 'multimedia' | 'settings';
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
  const displayName = userProfile?.first_name || user.username || user.email.split('@')[0];

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">SnapStudy</h1>
          <nav className="nav-tabs">
            <button 
              className={currentView === 'lessons' ? 'active' : ''}
              onClick={() => onViewChange('lessons')}
            >
              📚 Lessons
            </button>
            <button 
              className={currentView === 'multimedia' ? 'active' : ''}
              onClick={() => onViewChange('multimedia')}
            >
              🎵 Multimedia
            </button>
            <button 
              className={currentView === 'settings' ? 'active' : ''}
              onClick={() => onViewChange('settings')}
            >
              ⚙️ Settings
            </button>
          </nav>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <span className="welcome-text">Welcome, {displayName}</span>
            <div className="user-avatar">
              {displayName.charAt(0).toUpperCase()}
            </div>
          </div>
          <button className="logout-button" onClick={onLogout}>
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;