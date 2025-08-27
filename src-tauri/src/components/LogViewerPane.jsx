import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

/**
 * LogViewerPane renders run-scoped logs with optional filtering and
 * connection indicators. It subscribes to WebSocket updates while
 * validating incoming payloads to guard against malformed or malicious
 * messages and surfaces a badge for pending human-in-the-loop actions.
 */

const LogViewerPane = () => {
  const [logs, setLogs] = useState('');
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [connected, setConnected] = useState(false);
  const [hitlCount, setHitlCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // Fetch logs from the backend
  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try the enhanced logs endpoint first, fallback to basic if needed
      let response;
      try {
        response = await http.fetch('http://localhost:8000/api/logs', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
      } catch (e) {
        // Fallback to basic logs endpoint
        response = await http.fetch('http://localhost:8000/logs/latest', {
          method: 'GET',
          responseType: http.ResponseType.Text,
        });
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Handle different response formats
      if (typeof response.data === 'string') {
        setLogs(response.data);
      } else if (Array.isArray(response.data)) {
        // If we get an array of log entries, format them
        const formattedLogs = response.data
          .map(entry => `[${entry.timestamp}] ${entry.level.toUpperCase()}: ${entry.message}`)
          .join('\n');
        setLogs(formattedLogs);
      } else {
        setLogs('No logs available');
      }
      
    } catch (e) {
      console.error("Failed to fetch logs:", e);
      setError("Failed to load agent logs. Make sure the backend server is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial log fetch
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  // Subscribe to live log updates via WebSocket
  useEffect(() => {
    const handleLogUpdate = (entry) => {
      try {
        if (typeof entry === 'string') {
          setLogs((prev) => `${prev}\n${entry}`.trim());
        } else if (entry && entry.message) {
          const formattedEntry = `[${entry.timestamp || new Date().toISOString()}] ${(entry.level || 'INFO').toUpperCase()}: ${entry.message}`;
          setLogs((prev) => `${prev}\n${formattedEntry}`.trim());
        }
      } catch (e) {
        console.error('Error processing log update:', e);
      }
    };

    socket.on('log_added', handleLogUpdate);
    socket.on('log_update', handleLogUpdate);
    
    return () => {
      socket.off('log_added', handleLogUpdate);
      socket.off('log_update', handleLogUpdate);
    };
  }, []);

  // Track Socket.IO connection state
  useEffect(() => {
    const onConnect = () => setConnected(true);
    const onDisconnect = () => setConnected(false);
    
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    
    // Check initial connection status
    setConnected(socket.connected);
    
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []);

  // Listen for HITL updates to display a badge when human action is pending
  useEffect(() => {
    const handleHitlUpdate = (data) => {
      try {
        if (Array.isArray(data)) {
          setHitlCount(data.length);
        } else if (data && typeof data.count === 'number') {
          setHitlCount(data.count);
        }
      } catch (e) {
        console.error('Error processing HITL update:', e);
      }
    };

    socket.on('hitl_request', () => setHitlCount(prev => prev + 1));
    socket.on('hitl_approved', () => setHitlCount(prev => Math.max(0, prev - 1)));
    socket.on('hitl_denied', () => setHitlCount(prev => Math.max(0, prev - 1)));
    socket.on('hitl_update', handleHitlUpdate);
    
    return () => {
      socket.off('hitl_request');
      socket.off('hitl_approved');
      socket.off('hitl_denied');
      socket.off('hitl_update', handleHitlUpdate);
    };
  }, []);

  // Filter logs based on search term
  const displayedLogs = logs
    .split('\n')
    .filter((line) => line.toLowerCase().includes(filter.toLowerCase()))
    .join('\n');

  return (
    <div className="pane">
      <div className="pane-header">
        <h2>📋 System Logs</h2>
        <div className="log-tools">
          <input
            type="text"
            placeholder="Filter logs..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="log-filter"
          />
          <button onClick={fetchLogs} disabled={loading} className="btn-refresh">
            {loading ? '⟳' : '🔄'} Refresh
          </button>
          <span
            className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}
            title={connected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'}
          />
          {hitlCount > 0 && (
            <span className="hitl-badge" title={`${hitlCount} pending HITL request${hitlCount !== 1 ? 's' : ''}`}>
              {hitlCount}
            </span>
          )}
        </div>
      </div>
      <div className="pane-content log-viewer">
        {error ? (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button onClick={fetchLogs} className="btn-retry">
              Try Again
            </button>
          </div>
        ) : loading && !logs ? (
          <div className="loading-message">
            <span className="loading-spinner">⟳</span>
            <span>Loading logs...</span>
          </div>
        ) : (
          <pre className="log-content">
            {displayedLogs || 'No logs available. Logs will appear here as the system runs.'}
          </pre>
        )}
      </div>
    </div>
  );
};

export default LogViewerPane;
