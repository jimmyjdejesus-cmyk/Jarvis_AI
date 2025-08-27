import React, { useState, useCallback } from 'react';
import API_CONFIG, { getApiUrl } from '../config';

/**
 * Form for configuring Neo4j connection credentials.
 * Keeps credentials in memory and posts them to the backend
 * using the authenticated configuration endpoint.
 */
const Neo4jConfigForm = () => {
  const [uri, setUri] = useState('');
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState(null);

  const sendConfig = useCallback(async () => {
    try {
      const resp = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.NEO4J_CONFIG), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('jarvis-api-key') || '',
        },
        body: JSON.stringify({ uri, user, password }),
      });
      if (!resp.ok) {
        throw new Error('Failed to configure Neo4j');
      }
      setStatus('configured');
    } catch (err) {
      console.error('Failed to update Neo4j configuration:', err);
      setStatus('error');
    }
  }, [uri, user, password]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (uri && user && password) {
      sendConfig();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="neo4j-config-form">
      <div className="settings-section">
        <label>
          Neo4j URI:
          <input type="text" value={uri} onChange={(e) => setUri(e.target.value)} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          Neo4j User:
          <input type="text" value={user} onChange={(e) => setUser(e.target.value)} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          Neo4j Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
      </div>
      <button type="submit" className="btn-connect">
        Connect
      </button>
      {status === 'configured' && <div className="status success">Connected</div>}
      {status === 'error' && <div className="status error">Connection failed</div>}
    </form>
  );
};

export default Neo4jConfigForm;

