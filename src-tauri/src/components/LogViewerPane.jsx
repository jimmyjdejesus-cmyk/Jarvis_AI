import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

/**
 * LogViewerPane renders run-scoped logs with optional filtering and
 * connection indicators. It subscribes to WebSocket updates while
 * validating incoming payloads to guard against malformed or malicious
 * messages and surfaces a badge for pending human-in-the-loop actions.
 */
// The log viewer now exposes a connection status indicator, simple
// text filtering for log lines, and a badge showing pending
// human-in-the-loop (HITL) actions. These additions aim to make the
// debugging experience more transparent without requiring additional
// backend support.

// DEV-COMMENT: This component displays run-scoped logs produced by the
// `ScopedLogWriter`.  It queries the backend for the latest run transcript
// and provides a manual refresh button.

const LogViewerPane = () => {
  const [logs, setLogs] = useState('');
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [connected, setConnected] = useState(false);
  const [hitlCount, setHitlCount] = useState(0);

  // DEV-COMMENT: The 'useCallback' hook is used here to memoize the fetch function.
  // This prevents it from being recreated on every render, which is a good practice,
  // especially if this component were to become more complex.
  const fetchLogs = useCallback(async () => {
    try {
      const response = await http.fetch('http://127.0.0.1:8000/logs/latest', {
        method: 'GET',
        responseType: http.ResponseType.Text,
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // The response for logs is expected to be plain text.
      setLogs(response.data);
      setError(null);
    } catch (e) {
      console.error("Failed to fetch logs:", e);
      setError("Failed to load agent logs.");
    }
  }, []);

  // DEV-COMMENT: The useEffect hook calls fetchLogs when the component mounts
  // to load the initial log data. The dependency array includes fetchLogs
  // to ensure that if the function ever changed, it would be re-run.
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  // DEV-COMMENT: Subscribe to live log updates via WebSocket.
  useEffect(() => {
    const handler = (entry) => {
      if (typeof entry === 'string') {
        setLogs((prev) => `${prev}\n${entry}`.trim());
      }
    };
    socket.on('log_update', handler);
    return () => socket.off('log_update', handler);
  }, []);

  // Track Socket.IO connection state so that a small status indicator can
  // communicate whether live updates are flowing.
  useEffect(() => {
    const onConnect = () => setConnected(true);
    const onDisconnect = () => setConnected(false);
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []);

  // Listen for HITL updates to display a badge when human action is pending.
  useEffect(() => {
    const handler = (data) => {
      if (Array.isArray(data)) {
        setHitlCount(data.length);
      }
    };
    socket.on('hitl_update', handler);
    return () => socket.off('hitl_update', handler);
  }, []);

  const displayedLogs = logs
    .split('\n')
    .filter((line) => line.toLowerCase().includes(filter.toLowerCase()))
    .join('\n');

  return (
    <div className="pane">
      <div className="pane-header">
        <h2>Run Log</h2>
        <div className="log-tools">
          <input
            type="text"
            placeholder="Filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <button onClick={fetchLogs}>Refresh</button>
          <span
            className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}
            title={connected ? 'Connected' : 'Disconnected'}
          />
          {hitlCount > 0 && <span className="hitl-badge">{hitlCount}</span>}
        </div>
      </div>
      <div className="pane-content log-viewer">
        {error ? <p>{error}</p> : <pre>{displayedLogs || 'Loading logs...'}</pre>}
      </div>
    </div>
  );
};

export default LogViewerPane;