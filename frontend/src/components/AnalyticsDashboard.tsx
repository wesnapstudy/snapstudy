import React, { useState, useEffect } from 'react';
import { AnalyticsDashboard as AnalyticsDashboardType, User, LearningVelocity } from '../types';
import { analyticsService } from '../services/analyticsService';
import ProgressCharts from './ProgressCharts';
import PerformanceMetrics from './PerformanceMetrics';
import './AnalyticsDashboard.css';

interface AnalyticsDashboardProps {
  user: User;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ user }) => {
  const [dashboard, setDashboard] = useState<AnalyticsDashboardType | null>(null);
  const [velocity, setVelocity] = useState<LearningVelocity | null>(null);
  const [strugglingConcepts, setStrugglingConcepts] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(7);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all analytics data in parallel
      const [
        dashboardData,
        velocityData,
        strugglingData,
        recommendationsData
      ] = await Promise.all([
        analyticsService.getDashboard(),
        analyticsService.getLearningVelocity(selectedPeriod),
        analyticsService.getStrugglingConcepts(),
        analyticsService.getRecommendations()
      ]);

      setDashboard(dashboardData);
      setVelocity(velocityData);
      setStrugglingConcepts(strugglingData.struggling_concepts || []);
      setRecommendations(recommendationsData.recommendations || []);

    } catch (error) {
      console.error('Failed to load analytics data:', error);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatLearningPace = (pace: string): { text: string; color: string; icon: string } => {
    switch (pace) {
      case 'fast':
        return { text: 'Fast Learner', color: '#4CAF50', icon: '🚀' };
      case 'moderate':
        return { text: 'Steady Progress', color: '#FF9800', icon: '📈' };
      case 'slow':
        return { text: 'Taking Your Time', color: '#2196F3', icon: '🐢' };
      default:
        return { text: 'Getting Started', color: '#9E9E9E', icon: '🌱' };
    }
  };

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'mastered': return '#4CAF50';
      case 'comfortable': return '#8BC34A';
      case 'learning': return '#FF9800';
      case 'struggling': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high': return '#F44336';
      case 'medium': return '#FF9800';
      case 'low': return '#4CAF50';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <div className="analytics-dashboard loading">
        <div className="loading-spinner"></div>
        <p>Loading your learning analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard error">
        <div className="error-message">
          <h3>Unable to load analytics</h3>
          <p>{error}</p>
          <button onClick={loadAnalyticsData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboard || !velocity) {
    return (
      <div className="analytics-dashboard empty">
        <div className="empty-state">
          <h3>No analytics data available</h3>
          <p>Start learning to see your progress and analytics!</p>
        </div>
      </div>
    );
  }

  const paceInfo = formatLearningPace(velocity.learning_pace);

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2>Your Learning Analytics</h2>
        <div className="period-selector">
          <label>Time Period:</label>
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Key Metrics Cards */}
        <div className="metrics-row">
          <div className="metric-card">
            <div className="metric-icon">📚</div>
            <div className="metric-content">
              <div className="metric-value">{dashboard.metrics.lessons_completed}</div>
              <div className="metric-label">Lessons Completed</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🧠</div>
            <div className="metric-content">
              <div className="metric-value">{dashboard.metrics.quizzes_taken}</div>
              <div className="metric-label">Quizzes Taken</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">📊</div>
            <div className="metric-content">
              <div className="metric-value">{Math.round(dashboard.metrics.average_score)}%</div>
              <div className="metric-label">Average Score</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">⏱️</div>
            <div className="metric-content">
              <div className="metric-value">{Math.round(dashboard.metrics.total_time_spent_minutes)}</div>
              <div className="metric-label">Minutes Studied</div>
            </div>
          </div>
        </div>

        {/* Learning Velocity */}
        <div className="velocity-card">
          <h3>Learning Velocity</h3>
          <div className="velocity-content">
            <div className="pace-indicator" style={{ color: paceInfo.color }}>
              <span className="pace-icon">{paceInfo.icon}</span>
              <span className="pace-text">{paceInfo.text}</span>
            </div>
            
            <div className="velocity-stats">
              <div className="velocity-stat">
                <span className="stat-value">{velocity.daily_averages.lessons}</span>
                <span className="stat-label">Lessons/day</span>
              </div>
              <div className="velocity-stat">
                <span className="stat-value">{velocity.daily_averages.quizzes}</span>
                <span className="stat-label">Quizzes/day</span>
              </div>
              <div className="velocity-stat">
                <span className="stat-value">{Math.round(velocity.daily_averages.time_minutes)}</span>
                <span className="stat-label">Minutes/day</span>
              </div>
            </div>
            
            <div className="activity-score">
              <div className="activity-bar">
                <div 
                  className="activity-fill" 
                  style={{ width: `${Math.min(velocity.activity_score, 100)}%` }}
                ></div>
              </div>
              <span className="activity-label">
                Activity Score: {Math.round(velocity.activity_score)}/100
              </span>
            </div>
          </div>
        </div>

        {/* Retention Metrics */}
        <div className="retention-card">
          <h3>Learning Consistency</h3>
          <div className="retention-content">
            <div className="streak-info">
              <div className="streak-stat">
                <span className="streak-icon">🔥</span>
                <div className="streak-details">
                  <span className="streak-value">{dashboard.retention.current_streak}</span>
                  <span className="streak-label">Current Streak</span>
                </div>
              </div>
              
              <div className="streak-stat">
                <span className="streak-icon">🏅</span>
                <div className="streak-details">
                  <span className="streak-value">{dashboard.retention.longest_streak}</span>
                  <span className="streak-label">Best Streak</span>
                </div>
              </div>
            </div>
            
            <div className="consistency-metrics">
              <div className="consistency-item">
                <span className="consistency-label">Retention Rate</span>
                <span className="consistency-value">{dashboard.retention.retention_rate}%</span>
              </div>
              <div className="consistency-item">
                <span className="consistency-label">Consistency Score</span>
                <span className="consistency-value">{dashboard.retention.consistency_score}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Learning Patterns */}
        <div className="patterns-card">
          <h3>Learning Patterns</h3>
          <div className="patterns-content">
            {dashboard.learning_patterns.map((pattern, index) => (
              <div key={index} className="pattern-tag">
                {pattern.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            ))}
          </div>
        </div>

        {/* Progress Charts */}
        <div className="charts-section">
          <ProgressCharts 
            dashboard={dashboard}
            velocity={velocity}
          />
        </div>

        {/* Performance Metrics */}
        <div className="performance-section">
          <PerformanceMetrics 
            dashboard={dashboard}
            strugglingConcepts={strugglingConcepts}
          />
        </div>

        {/* Struggling Concepts */}
        {strugglingConcepts.length > 0 && (
          <div className="struggling-concepts-card">
            <h3>Areas for Improvement</h3>
            <div className="concepts-list">
              {strugglingConcepts.slice(0, 5).map((concept, index) => (
                <div key={index} className="concept-item">
                  <div className="concept-info">
                    <span className="concept-name">{concept.concept}</span>
                    <span className="concept-score">{Math.round(concept.recent_average)}%</span>
                  </div>
                  <div className="concept-details">
                    <span className="attempts">Attempts: {concept.attempts}</span>
                    <span className={`trend ${concept.improvement_trend}`}>
                      {concept.improvement_trend === 'improving' ? '📈' : '📉'} {concept.improvement_trend}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="recommendations-card">
            <h3>Personalized Recommendations</h3>
            <div className="recommendations-list">
              {recommendations.map((rec, index) => (
                <div 
                  key={index} 
                  className={`recommendation-item priority-${rec.priority}`}
                  style={{ borderLeftColor: getPriorityColor(rec.priority) }}
                >
                  <div className="recommendation-header">
                    <span className="recommendation-title">{rec.title}</span>
                    <span className={`priority-badge priority-${rec.priority}`}>
                      {rec.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="recommendation-description">{rec.description}</p>
                  <div className="recommendation-meta">
                    <span className="recommendation-type">{rec.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="dashboard-footer">
        <p className="last-updated">
          Last updated: {new Date(dashboard.generated_at).toLocaleString()}
        </p>
        <button onClick={loadAnalyticsData} className="refresh-button">
          🔄 Refresh Data
        </button>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;