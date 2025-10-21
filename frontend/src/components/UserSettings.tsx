import React, { useState } from 'react';
import { User, UserProfile } from '../types';
import AnalyticsDashboard from './AnalyticsDashboard';

interface UserSettingsProps {
  user: User;
  userProfile: UserProfile | null;
  onProfileUpdate: (profile: UserProfile) => void;
  onLogout: () => void;
}

// SVG Icons matching lessons page style
const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
  </svg>
);

const AnalyticsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
  </svg>
);

const LogoutIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
  </svg>
);

const EditIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
  </svg>
);

const SaveIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>
  </svg>
);

const UserSettings: React.FC<UserSettingsProps> = ({
  user,
  userProfile,
  onProfileUpdate,
  onLogout
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'analytics'>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
    age: user.age || '',
    profession: user.profession || '',
    education_level: user.education_level || '',
    country: user.country || '',
    learning_style: user.preferences?.learning_style || 'visual',
    attention_span: user.preferences?.attention_span || 15,
    difficulty_level: user.preferences?.difficulty_level || 'intermediate'
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    // TODO: Call API to save profile changes
    console.log('Saving profile:', formData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    // Reset form to original values
    setFormData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      age: user.age || '',
      profession: user.profession || '',
      education_level: user.education_level || '',
      country: user.country || '',
      learning_style: user.preferences?.learning_style || 'visual',
      attention_span: user.preferences?.attention_span || 15,
      difficulty_level: user.preferences?.difficulty_level || 'intermediate'
    });
    setIsEditing(false);
  };

  return (
    <div className="user-settings-container">
      <div className="profile-tabs">
        <button
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <span className="tab-icon"><UserIcon /></span>
          <span>Profile</span>
        </button>
        <button
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <span className="tab-icon"><AnalyticsIcon /></span>
          <span>Analytics</span>
        </button>
        <button
          className="tab-button logout-tab"
          onClick={onLogout}
        >
          <span className="tab-icon"><LogoutIcon /></span>
          <span>Logout</span>
        </button>
      </div>

      {activeTab === 'profile' ? (
        <div className="profile-content">
          <div className="profile-header">
            <div className="profile-avatar">
              <div className="avatar-circle">
                {(formData.first_name?.[0] || 'U').toUpperCase()}
              </div>
            </div>
            <div className="profile-title">
              <h2>{formData.first_name} {formData.last_name}</h2>
              <p className="profile-email">{formData.email}</p>
            </div>
            <button
              className="edit-profile-btn"
              onClick={() => isEditing ? handleSave() : setIsEditing(true)}
            >
              <span className="btn-icon">
                {isEditing ? <SaveIcon /> : <EditIcon />}
              </span>
              <span>{isEditing ? 'Save' : 'Edit'}</span>
            </button>
          </div>

          <div className="profile-form">
            <div className="form-section">
              <h3>Personal Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="First Name"
                  />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Last Name"
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Email"
                  />
                </div>
                <div className="form-group">
                  <label>Age</label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Age"
                  />
                </div>
                <div className="form-group">
                  <label>Profession</label>
                  <input
                    type="text"
                    name="profession"
                    value={formData.profession}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Profession"
                  />
                </div>
                <div className="form-group">
                  <label>Education Level</label>
                  <select
                    name="education_level"
                    value={formData.education_level}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                  >
                    <option value="">Select Education Level</option>
                    <option value="High School">High School</option>
                    <option value="Undergraduate">Undergraduate</option>
                    <option value="Graduate">Graduate</option>
                    <option value="Doctorate">Doctorate</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Country</label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    placeholder="Country"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Learning Preferences</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Learning Style</label>
                  <select
                    name="learning_style"
                    value={formData.learning_style}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                  >
                    <option value="visual">Visual</option>
                    <option value="auditory">Auditory</option>
                    <option value="reading">Reading/Writing</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Attention Span (minutes)</label>
                  <input
                    type="number"
                    name="attention_span"
                    value={formData.attention_span}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    min="5"
                    max="60"
                  />
                </div>
                <div className="form-group">
                  <label>Difficulty Level</label>
                  <select
                    name="difficulty_level"
                    value={formData.difficulty_level}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
            </div>

            {isEditing && (
              <div className="form-actions">
                <button className="btn-cancel" onClick={handleCancel}>
                  Cancel
                </button>
                <button className="btn-save" onClick={handleSave}>
                  Save Changes
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="analytics-content">
          <AnalyticsDashboard user={user} />
        </div>
      )}
    </div>
  );
};

export default UserSettings;