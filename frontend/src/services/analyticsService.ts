class AnalyticsService {
  recordMetric(name: string, value: number, metadata?: Record<string, any>): void {
    // Simple analytics recording - in production this would send to a real analytics service
    console.log(`Analytics: ${name} = ${value}`, metadata);
    
    // Store locally for now
    const analytics = JSON.parse(localStorage.getItem('analytics') || '[]');
    analytics.push({
      name,
      value,
      metadata,
      timestamp: new Date().toISOString()
    });
    
    // Keep only last 100 events
    if (analytics.length > 100) {
      analytics.splice(0, analytics.length - 100);
    }
    
    localStorage.setItem('analytics', JSON.stringify(analytics));
  }

  getMetrics(): any[] {
    return JSON.parse(localStorage.getItem('analytics') || '[]');
  }
}

export const analyticsService = new AnalyticsService();