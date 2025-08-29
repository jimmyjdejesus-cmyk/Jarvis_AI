let authToken = localStorage.getItem('jarvis-auth-token') || null;

/**
 * Initialize global fetch wrappers to include Authorization header when a token exists.
 * Also patches Tauri's http.fetch for desktop builds.
 */
export async function initAuth() {
  // Patch browser fetch
  const originalFetch = window.fetch;
  window.fetch = async (input, options = {}) => {
    const headers = new Headers(options.headers || {});
    if (authToken) {
      headers.set('Authorization', `Bearer ${authToken}`);
    }
    return originalFetch(input, { ...options, headers });
  };

  // Patch Tauri http.fetch if available
  try {
    const { http } = await import('@tauri-apps/api');
    const originalHttpFetch = http.fetch;
    http.fetch = async (url, options = {}) => {
      const headers = { ...(options.headers || {}) };
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      return originalHttpFetch(url, { ...options, headers });
    };
  } catch (e) {
    // Tauri APIs not available (e.g., during tests)
  }
}

export function setAuthToken(token) {
  authToken = token;
  if (token) {
    localStorage.setItem('jarvis-auth-token', token);
  } else {
    localStorage.removeItem('jarvis-auth-token');
  }
}

export function getAuthToken() {
  return authToken;
}
