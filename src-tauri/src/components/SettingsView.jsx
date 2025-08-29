import React, { useState } from 'react';
import API_CONFIG, { setBackendBaseUrl, setApiKey, TEAM_SETTINGS, setTeamSetting } from '../config';

const SettingsView = () => {
  const [backendUrl, updateBackendUrl] = useState(API_CONFIG.HTTP_BASE_URL);
  const [apiKey, updateApiKey] = useState(API_CONFIG.API_KEY);
  const [neo4jUri, setNeo4jUri] = useState(localStorage.getItem('jarvis-neo4j-uri') || '');
  const [neo4jUser, setNeo4jUser] = useState(localStorage.getItem('jarvis-neo4j-user') || '');
  const [neo4jPassword, setNeo4jPassword] = useState(localStorage.getItem('jarvis-neo4j-password') || '');
  const [activeTab, setActiveTab] = useState('general');
  const [blackTeam, setBlackTeam] = useState(TEAM_SETTINGS.Black);

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

  const handleBlackChange = (key) => (e) => {
    const value = Number(e.target.value);
    setBlackTeam((prev) => ({ ...prev, [key]: value }));
    setTeamSetting('Black', key, value);
  };

  return (
      <div className="settings-view">
        <h1>Settings</h1>
        <div className="settings-tabs">
          <button
            className={activeTab === 'general' ? 'active' : ''}
            onClick={() => setActiveTab('general')}
          >
            General
          </button>
          <button
            className={activeTab === 'teams' ? 'active' : ''}
            onClick={() => setActiveTab('teams')}
          >
            Teams
          </button>
        </div>

        {activeTab === 'general' && (
          <>
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
          </>
        )}

        {activeTab === 'teams' && (
          <div className="team-settings">
            <div className="team-section black-team">
              <h2>Black Team</h2>
              <label>
                Curiosity:
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={blackTeam.curiosity}
                  onChange={handleBlackChange('curiosity')}
                />
                {blackTeam.curiosity}
              </label>
              <label>
                Risk vs Reward:
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={blackTeam.riskReward}
                  onChange={handleBlackChange('riskReward')}
                />
                {blackTeam.riskReward}
              </label>
              <label>
                Token Usage:
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={blackTeam.tokenUsage}
                  onChange={handleBlackChange('tokenUsage')}
                />
                {blackTeam.tokenUsage}
              </label>
              <label>
                Computation Usage:
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={blackTeam.computeUsage}
                  onChange={handleBlackChange('computeUsage')}
                />
                {blackTeam.computeUsage}
              </label>
            </div>
          </div>
        )}
      </div>
    );
  };

export default SettingsView;
