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
    <header className="snap-header">
      <div className="brand">
        <img src="/weblogo.png" alt="SnapStudy logo" />
        <span>SnapStudy</span>
      </div>
      <nav>
        <button 
          className={currentView === 'lessons' ? 'active' : ''}
          onClick={() => onViewChange('lessons')}
        >
          Dashboard
        </button>
        <button 
          className={currentView === 'multimedia' ? 'active' : ''}
          onClick={() => onViewChange('multimedia')}
        >
          Analytics
        </button>
      </nav>
    </header>
  );
};

export default Header;