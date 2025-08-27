import React, { useState, useEffect } from 'react';
import API_CONFIG, { getApiUrl, setBackendBaseUrl, getHealthStatus } from '../config';

const MissionHistoryView = () => {
  const [missionId, setMissionId] = useState('');
  const [history, setHistory] = useState(null);
  const [error, setError] = useState(null);
  const [backendUrl, setBackendUrl] = useState(API_CONFIG.HTTP_BASE_URL);
  const [backendStatus, setBackendStatus] = useState(false);
  const [neo4jStatus, setNeo4jStatus] = useState(false);

  useEffect(() => {
    refreshStatus();
  }, []);

  const refreshStatus = async () => {
    const status = await getHealthStatus();
    setBackendStatus(status.backend);
    setNeo4jStatus(status.neo4j);
  };

  const applyBackendUrl = () => {
    setError(null);
    const trimmed = backendUrl.trim();
    if (!/^https?:\/\//i.test(trimmed)) {
      setError('Invalid backend URL');
      return;
    }
    setBackendBaseUrl(trimmed);
    setBackendUrl(trimmed);
    refreshStatus();
  };

  const fetchHistory = async () => {
    setError(null);
    setHistory(null);
    const sanitized = missionId.replace(/[^\w-]/g, '');
    if (!sanitized) {
      setError('Please enter a valid mission ID.');
      return;
    }
    try {
      const res = await fetch(getApiUrl(`/missions/${encodeURIComponent(sanitized)}/history`));
      if (!res.ok) {
        throw new Error('Request failed');
      }
      const data = await res.json();
      setHistory(data);
    } catch (e) {
      console.error(e);
      setError('Failed to fetch mission history');
    }
  };

  return (
    <div className="mission-history-view">
      <div className="mission-history-controls">
        <div className="connection-config">
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            placeholder="Backend URL"
          />
          <button onClick={applyBackendUrl}>Set URL</button>
          <div className={`connection-status ${backendStatus ? 'connected' : 'disconnected'}`}>
            <span className="status-indicator"></span>
            Backend {backendStatus ? 'Online' : 'Offline'}
          </div>
          <div className={`connection-status ${neo4jStatus ? 'connected' : 'disconnected'}`}>
            <span className="status-indicator"></span>
            Neo4j {neo4jStatus ? 'Online' : 'Offline'}
          </div>
        </div>
        <input
          type="text"
          value={missionId}
          onChange={(e) => setMissionId(e.target.value)}
          placeholder="Mission ID"
        />
        <button onClick={fetchHistory}>Load History</button>
      </div>
      {error && <p className="error-message">{error}</p>}
      {history && (
        <pre className="mission-history-output">
          {JSON.stringify(history, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default MissionHistoryView;
