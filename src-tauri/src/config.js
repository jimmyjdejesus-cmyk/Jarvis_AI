// Centralized configuration for backend API endpoints
const storedHttp = localStorage.getItem('jarvis-backend-url') || 'http://localhost:8000';
const storedWs = localStorage.getItem('jarvis-backend-ws') || 'ws://localhost:8000';

const API_CONFIG = {
  // Backend base URLs
  HTTP_BASE_URL: storedHttp,
  WS_BASE_URL: storedWs,
  
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

// Update backend base URL at runtime
export const setBackendBaseUrl = (url) => {
  API_CONFIG.HTTP_BASE_URL = url;
  API_CONFIG.WS_BASE_URL = url.replace(/^http/i, 'ws');
  localStorage.setItem('jarvis-backend-url', API_CONFIG.HTTP_BASE_URL);
  localStorage.setItem('jarvis-backend-ws', API_CONFIG.WS_BASE_URL);
};

// Fetch backend and Neo4j health status
export const getHealthStatus = async () => {
  try {
    const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.HEALTH));
    if (!response.ok) {
      return { backend: false, neo4j: false };
    }
    const data = await response.json();
    return { backend: true, neo4j: Boolean(data.neo4j_active) };
  } catch (error) {
    console.error('Health check failed:', error);
    return { backend: false, neo4j: false };
  }
};

export default API_CONFIG;
