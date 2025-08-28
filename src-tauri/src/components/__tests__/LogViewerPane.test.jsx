import React, { useState } from 'react';

import API_CONFIG, { setBackendBaseUrl, setApiKey, setServiceCredential, TEAM_SETTINGS, setTeamSetting } from '../config';

const SettingsView = () => {
  const [backendUrl, updateBackendUrl] = useState(API_CONFIG.HTTP_BASE_URL);
  const [apiKey, updateApiKey] = useState(API_CONFIG.API_KEY);
  const [neo4jUri, setNeo4jUri] = useState(localStorage.getItem('jarvis-neo4j-uri') || '');
  const [neo4jUser, setNeo4jUser] = useState(localStorage.getItem('jarvis-neo4j-user') || '');
  const [neo4jPassword, setNeo4jPassword] = useState(localStorage.getItem('jarvis-neo4j-password') || '');

  const [openaiKey, setOpenaiKey] = useState(localStorage.getItem('jarvis-openai-key') || '');
  const [anthropicKey, setAnthropicKey] = useState(localStorage.getItem('jarvis-anthropic-key') || '');

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


  const handleOpenaiKeyChange = (e) => {

    const value = e.target.value;

    setOpenaiKey(value);

    localStorage.setItem('jarvis-openai-key', value);

    setServiceCredential('OPENAI_API_KEY', value);

  };


  const handleAnthropicKeyChange = (e) => {

    const value = e.target.value;

    setAnthropicKey(value);

    localStorage.setItem('jarvis-anthropic-key', value);

    setServiceCredential('ANTHROPIC_API_KEY', value);

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