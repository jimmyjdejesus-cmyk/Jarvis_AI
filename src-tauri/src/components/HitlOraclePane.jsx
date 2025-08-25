import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

// DEV-COMMENT: This component displays Human-in-the-Loop (HITL) recommendations.
// These are decision points where the system requires user input to proceed.
// It fetches this data from the backend and renders it as a list of actionable items.

const HitlOraclePane = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);

  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await http.fetch('http://127.0.0.1:8000/api/hitl');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setRecommendations(response.data);
      setError(null);
    } catch (e) {
      console.error("Failed to fetch HITL recommendations:", e);
      setError("Failed to load HITL recommendations.");
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  // DEV-COMMENT: Receive HITL updates in real time via WebSocket.
  useEffect(() => {
    const handler = (data) => {
      setRecommendations(data);
    };
    socket.on('hitl_update', handler);
    return () => socket.off('hitl_update', handler);
  }, []);

  return (
    <div className="pane">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>HITL Oracle</h2>
        <button onClick={fetchRecommendations}>Refresh</button>
      </div>
      <div className="pane-content">
        {error && <p>{error}</p>}
        {recommendations.length > 0 ? (
          recommendations.map((item) => (
            <div key={item.id} className="hitl-item">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <div>
                {item.actions.map((action) => (
                  <button key={action} style={{ marginRight: '0.5rem' }}>
                    {action}
                  </button>
                ))}
              </div>
            </div>
          ))
        ) : (
          <p>No pending recommendations.</p>
        )}
      </div>
    </div>
  );
};

export default HitlOraclePane;
