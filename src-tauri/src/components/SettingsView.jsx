import React, { useState } from 'react';
import API_CONFIG, { setBackendBaseUrl, setApiKey } from '../config';

const SettingsView = () => {
  const [backendUrl, updateBackendUrl] = useState(API_CONFIG.HTTP_BASE_URL);
  const [apiKey, updateApiKey] = useState(API_CONFIG.API_KEY);
  const [neo4jUri, setNeo4jUri] = useState(localStorage.getItem('jarvis-neo4j-uri') || '');
  const [neo4jUser, setNeo4jUser] = useState(localStorage.getItem('jarvis-neo4j-user') || '');
  const [neo4jPassword, setNeo4jPassword] = useState(localStorage.getItem('jarvis-neo4j-password') || '');

  const handleBackendChange = (e) => {
    const value = e.target.value;
    updateBackendUrl(value);
    setBackendBaseUrl(value);
  };

  const handleApiKeyChange = (e) => {
    const value = e.target.value;
    updateApiKey(value);
    setApiKey(value);
  };

  const handleNeo4jUriChange = (e) => {
    const value = e.target.value;
    setNeo4jUri(value);
    localStorage.setItem('jarvis-neo4j-uri', value);
  };

  const handleNeo4jUserChange = (e) => {
    const value = e.target.value;
    setNeo4jUser(value);
    localStorage.setItem('jarvis-neo4j-user', value);
  };

  const handleNeo4jPasswordChange = (e) => {
    const value = e.target.value;
    setNeo4jPassword(value);
    localStorage.setItem('jarvis-neo4j-password', value);
  };

  return (
    <div className="settings-view">
      <h1>Settings</h1>
      <div className="settings-section">
        <label>
          Backend URL:
          <input type="text" value={backendUrl} onChange={handleBackendChange} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          API Key:
          <input type="text" value={apiKey} onChange={handleApiKeyChange} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          Neo4j URI:
          <input type="text" value={neo4jUri} onChange={handleNeo4jUriChange} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          Neo4j User:
          <input type="text" value={neo4jUser} onChange={handleNeo4jUserChange} />
        </label>
      </div>
      <div className="settings-section">
        <label>
          Neo4j Password:
          <input type="password" value={neo4jPassword} onChange={handleNeo4jPasswordChange} />
        </label>
      </div>
    </div>
  );
};

export default SettingsView;
