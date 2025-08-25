import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

// DEV-COMMENT: This component displays run-scoped logs produced by the
// `ScopedLogWriter`.  It queries the backend for the latest run transcript
// and provides a manual refresh button.

const LogViewerPane = () => {
  const [logs, setLogs] = useState('');
  const [error, setError] = useState(null);

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
      setLogs((prev) => `${prev}\n${entry}`.trim());
    };
    socket.on('log_update', handler);
    return () => socket.off('log_update', handler);
  }, []);

  return (
    <div className="pane">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Run Log</h2>
        <button onClick={fetchLogs}>Refresh</button>
      </div>
      <div className="pane-content log-viewer">
        {error ? (
          <p>{error}</p>
        ) : (
          <pre>{logs || 'Loading logs...'}</pre>
        )}
      </div>
    </div>
  );
};

export default LogViewerPane;
