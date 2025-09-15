import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 404) {
        throw new Error('Resource not found');
      } else if (status === 500) {
        throw new Error('Internal server error. Please try again later.');
      } else if (data?.detail) {
        throw new Error(data.detail);
      } else {
        throw new Error(`HTTP ${status}: ${error.message}`);
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error. Please check your connection and try again.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export const apiService = {
  // Health check
  async getHealth() {
    return apiClient.get('/health');
  },

  // Timeline and events
  async getTimeline(stockSymbol = null, startDate = null, endDate = null, eventTypes = null, limit = 100) {
    const params = new URLSearchParams();
    
    if (stockSymbol) params.append('stock_symbol', stockSymbol);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (eventTypes) params.append('event_types', eventTypes.join(','));
    if (limit) params.append('limit', limit.toString());

    return apiClient.get(`/timeline?${params.toString()}`);
  },

  // Reports
  async generateReport(requestData) {
    return apiClient.post('/reports/generate', requestData);
  },

  async getReportStatus(jobId) {
    return apiClient.get(`/reports/status/${jobId}`);
  },

  async getReports(stockSymbol = null, status = null, limit = 50, offset = 0) {
    const params = new URLSearchParams();
    
    if (stockSymbol) params.append('stock_symbol', stockSymbol);
    if (status) params.append('status', status);
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());

    return apiClient.get(`/reports?${params.toString()}`);
  },

  async getReport(reportId) {
    return apiClient.get(`/reports/${reportId}`);
  },

  // Mock data for development/testing
  async getMockData() {
    // Return mock data when backend is not available
    return {
      timeline: [
        {
          id: 1,
          type: 'market_data',
          date: new Date('2024-01-15T09:30:00'),
          title: 'AAPL Stock Price Movement',
          description: 'Apple Inc. stock dropped 3.2% in morning trading',
          stockSymbols: ['AAPL'],
          metadata: {
            priceChange: -3.2,
            volume: 45000000,
            price: 185.64
          }
        },
        {
          id: 2,
          type: 'sec_filing',
          date: new Date('2024-01-15T08:00:00'),
          title: 'AAPL Files 8-K Form',
          description: 'Apple Inc. filed an 8-K form regarding executive compensation changes',
          stockSymbols: ['AAPL'],
          metadata: {
            filingType: '8-K',
            accessionNumber: '0000320193-24-000001'
          }
        }
      ],
      reports: [
        {
          id: 1,
          title: 'Correlation Analysis: AAPL Price Drop and SEC Filing',
          content: `DISCLAIMER: This analysis is AI-generated and not financial advice.

EXECUTIVE SUMMARY:
A correlation analysis was performed on Apple Inc. (AAPL) stock following a 3.2% price decline that coincided with an 8-K SEC filing regarding executive compensation changes.

KEY FINDINGS:
1. TEMPORAL CORRELATION: The stock price decline occurred within 90 minutes of the SEC filing becoming public.

2. VOLUME ANALYSIS: Trading volume increased 145% above the 30-day average during the decline period.

3. NEWS SENTIMENT: No significant negative news coverage detected in the same timeframe, suggesting the SEC filing may have contributed to the price movement.

CORRELATIONS IDENTIFIED:
- SEC Filing Time: 08:00 EST
- Price Decline Start: 09:30 EST (market open)
- Maximum Decline: 09:45 EST (-3.2%)
- Volume Spike: 300% above normal at 09:45 EST

CONFIDENCE LEVEL: Medium (65%)
The temporal proximity and lack of other significant negative catalysts suggest a potential correlation, but correlation does not imply causation.

DISCLAIMER: This analysis is for educational purposes only and should not be used as the sole basis for investment decisions.`,
          confidence_score: 0.65,
          status: 'published',
          generated_at: '2024-01-15T10:30:00Z',
          correlations_found: {
            'temporal_correlation': {
              'filing_time': '08:00:00',
              'price_decline_start': '09:30:00',
              'correlation_strength': 0.65
            },
            'volume_correlation': {
              'normal_volume': 31000000,
              'spike_volume': 45000000,
              'increase_percentage': 145
            }
          },
          data_sources: {
            'market_data_points': 48,
            'sec_filings': 1,
            'news_articles': 12
          }
        }
      ]
    };
  }
};

export default apiService;