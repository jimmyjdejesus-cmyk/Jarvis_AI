// Centralized configuration for backend API endpoints
const API_CONFIG = {
  // Backend base URLs
  HTTP_BASE_URL: 'http://localhost:8000',
  WS_BASE_URL: 'ws://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    WORKFLOW: (sessionId) => `/api/workflow/${sessionId}`,
    WORKFLOW_SIMULATE: (sessionId) => `/api/workflow/${sessionId}/simulate`,
    LOGS: '/api/logs',
    LOGS_LATEST: '/logs/latest',
    HITL_PENDING: '/api/hitl/pending',
    HITL_APPROVE: (requestId) => `/api/hitl/${requestId}/approve`,
    HITL_DENY: (requestId) => `/api/hitl/${requestId}/deny`,
    DEAD_ENDS: (sessionId) => `/api/dead-ends?session_id=${sessionId}`,
    DEAD_END_RETRY: (taskId) => `/api/dead-ends/${taskId}/retry`,
    HEALTH: '/health'
  }
};

// Helper function to build full API URLs
export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.HTTP_BASE_URL}${endpoint}`;
};

// Helper function to get WebSocket URL
export const getWebSocketUrl = () => {
  return API_CONFIG.WS_BASE_URL;
};

// Test backend connectivity
export const testBackendConnection = async () => {
  try {
    const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.HEALTH));
    return response.ok;
  } catch (error) {
    console.error('Backend connection test failed:', error);
    return false;
  }
};

export default API_CONFIG;
