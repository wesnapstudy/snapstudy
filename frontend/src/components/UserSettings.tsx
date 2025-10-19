import React, { useState } from 'react';
import { User, UserProfile } from '../types';
import './UserSettings.css';

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
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences'>('profile');
  const [formData, setFormData] = useState({
    first_name: userProfile?.first_name || '',
    last_name: userProfile?.last_name || '',
    username: userProfile?.username || '',
    theme: userProfile?.preferences?.theme || 'light',
    language: userProfile?.preferences?.language || 'en',
    notifications_enabled: userProfile?.preferences?.notifications_enabled ?? true,
    auto_play_videos: userProfile?.preferences?.auto_play_videos ?? true,
    playback_speed: userProfile?.preferences?.playback_speed || 1.0
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSave = () => {
    // In a real app, this would make an API call
    console.log('Saving profile:', formData);
  };

  return (
    <div className="user-settings">
      <div className="settings-header">
        <h2>⚙️ Settings</h2>
      </div>

      <div className="settings-tabs">
        <button 
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          👤 Profile
        </button>
        <button 
          className={activeTab === 'preferences' ? 'active' : ''}
          onClick={() => setActiveTab('preferences')}
        >
          🎛️ Preferences
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'profile' && (
          <div className="profile-section">
            <div className="profile-avatar-section">
              <div className="profile-avatar">
                {(formData.first_name || user.email).charAt(0).toUpperCase()}
              </div>
              <div className="profile-info">
                <h3>{formData.first_name} {formData.last_name}</h3>
                <p>{user.email}</p>
              </div>
            </div>

            <div className="form-section">
              <h4>Personal Information</h4>
              <div className="form-grid">
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    placeholder="Enter your first name"
                  />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    placeholder="Enter your last name"
                  />
                </div>
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    placeholder="Choose a username"
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="disabled-input"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'preferences' && (
          <div className="preferences-section">
            <div className="form-section">
              <h4>Appearance</h4>
              <div className="form-group">
                <label>Theme</label>
                <select
                  name="theme"
                  value={formData.theme}
                  onChange={handleInputChange}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
              <div className="form-group">
                <label>Language</label>
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleInputChange}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
            </div>

            <div className="form-section">
              <h4>Learning Preferences</h4>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="auto_play_videos"
                    checked={formData.auto_play_videos}
                    onChange={handleInputChange}
                  />
                  <span className="checkmark"></span>
                  Auto-play videos
                </label>
              </div>
              <div className="form-group">
                <label>Default Playback Speed</label>
                <select
                  name="playback_speed"
                  value={formData.playback_speed}
                  onChange={handleInputChange}
                >
                  <option value={0.5}>0.5x</option>
                  <option value={0.75}>0.75x</option>
                  <option value={1.0}>1.0x (Normal)</option>
                  <option value={1.25}>1.25x</option>
                  <option value={1.5}>1.5x</option>
                  <option value={2.0}>2.0x</option>
                </select>
              </div>
            </div>

            <div className="form-section">
              <h4>Notifications</h4>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="notifications_enabled"
                    checked={formData.notifications_enabled}
                    onChange={handleInputChange}
                  />
                  <span className="checkmark"></span>
                  Enable notifications
                </label>
              </div>
            </div>
          </div>
        )}

        <div className="settings-actions">
          <button className="save-button" onClick={handleSave}>
            💾 Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings;