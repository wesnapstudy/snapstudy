import React from 'react';
import { User, UserProfile } from '../types';

interface UserSettingsProps {
  user: User;
  userProfile: UserProfile | null;
  onProfileUpdate: (profile: UserProfile) => void;
}

const UserSettings: React.FC<UserSettingsProps> = ({ 
  user, 
  userProfile, 
  onProfileUpdate 
}) => {
  return (
    <div className="user-settings">
      <h2>Settings</h2>
      
      <div className="settings-section">
        <h3>Profile Information</h3>
        <div className="profile-info">
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
        </div>
      </div>
      
      <div className="settings-section">
        <h3>Learning Preferences</h3>
        <p>Customize your learning experience (coming soon)</p>
      </div>
      
      <div className="settings-section">
        <h3>Account Settings</h3>
        <p>Manage your account settings (coming soon)</p>
      </div>
    </div>
  );
};

export default UserSettings;