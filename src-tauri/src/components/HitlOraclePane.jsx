import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

// DEV-COMMENT: This component displays Human-in-the-Loop (HITL) recommendations.
// These are decision points where the system requires user input to proceed.
// It fetches this data from the backend and renders it as a list of actionable items.

const HitlOraclePane = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);

  const fetchRecommendations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try the enhanced HITL endpoint
      const response = await http.fetch('http://localhost:8000/api/hitl/pending', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      setRecommendations(response.data || []);
    } catch (e) {
      console.error("Failed to fetch HITL recommendations:", e);
      setError("Failed to load HITL recommendations. Make sure the backend server is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  // Receive HITL updates in real time via WebSocket
  useEffect(() => {
    const handleHitlRequest = (data) => {
      console.log('HITL request received:', data);
      setRecommendations(prev => [...prev, data]);
    };

    const handleHitlApproved = (data) => {
      console.log('HITL approved:', data);
      setRecommendations(prev => 
        prev.filter(item => item.id !== data.request_id)
      );
    };

    const handleHitlDenied = (data) => {
      console.log('HITL denied:', data);
      setRecommendations(prev => 
        prev.filter(item => item.id !== data.request_id)
      );
    };

    const handleHitlUpdate = (data) => {
      console.log('HITL update received:', data);
      if (Array.isArray(data)) {
        setRecommendations(data);
      }
    };

    socket.on('hitl_request', handleHitlRequest);
    socket.on('hitl_approved', handleHitlApproved);
    socket.on('hitl_denied', handleHitlDenied);
    socket.on('hitl_update', handleHitlUpdate);
    
    return () => {
      socket.off('hitl_request', handleHitlRequest);
      socket.off('hitl_approved', handleHitlApproved);
      socket.off('hitl_denied', handleHitlDenied);
      socket.off('hitl_update', handleHitlUpdate);
    };
  }, []);

  // Track connection status
  useEffect(() => {
    const onConnect = () => setConnected(true);
    const onDisconnect = () => setConnected(false);
    
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    
    setConnected(socket.connected);
    
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []);

  // Handle HITL action (approve/deny)
  const handleHitlAction = useCallback(async (requestId, action, response = null) => {
    try {
      const endpoint = action === 'approve' 
        ? `http://localhost:8000/api/hitl/${requestId}/approve`
        : `http://localhost:8000/api/hitl/${requestId}/deny`;
      
      const result = await http.fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: response ? JSON.stringify(response) : JSON.stringify({ reason: 'User decision' }),
      });

      if (!result.ok) {
        throw new Error(`Failed to ${action} HITL request`);
      }

      // Remove the request from local state (will also be updated via WebSocket)
      setRecommendations(prev => 
        prev.filter(item => item.id !== requestId)
      );

    } catch (e) {
      console.error(`Failed to ${action} HITL request:`, e);
      setError(`Failed to ${action} request. Please try again.`);
    }
  }, []);

  return (
    <div className="pane">
      <div className="pane-header">
        <h2>🤝 HITL Oracle</h2>
        <div className="hitl-controls">
          <span
            className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}
            title={connected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'}
          />
          <button onClick={fetchRecommendations} disabled={loading} className="btn-refresh">
            {loading ? '⟳' : '🔄'} Refresh
          </button>
          {recommendations.length > 0 && (
            <span className="hitl-count">
              {recommendations.length} pending
            </span>
          )}
        </div>
      </div>
      <div className="pane-content">
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button onClick={fetchRecommendations} className="btn-retry">
              Try Again
            </button>
          </div>
        )}
        
        {loading && recommendations.length === 0 ? (
          <div className="loading-message">
            <span className="loading-spinner">⟳</span>
            <span>Loading HITL requests...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="hitl-list">
            {recommendations.map((item) => (
              <div key={item.id} className="hitl-item">
                <div className="hitl-header">
                  <h3>{item.prompt || item.title || 'Human Input Required'}</h3>
                  <span className="hitl-type">{item.type || 'decision'}</span>
                </div>
                
                {item.context && Object.keys(item.context).length > 0 && (
                  <div className="hitl-context">
                    <strong>Context:</strong>
                    <pre>{JSON.stringify(item.context, null, 2)}</pre>
                  </div>
                )}
                
                <div className="hitl-actions">
                  {item.options && item.options.length > 0 ? (
                    item.options.map((option) => (
                      <button
                        key={option}
                        onClick={() => handleHitlAction(item.id, 'approve', { choice: option })}
                        className="btn-hitl-option"
                      >
                        {option}
                      </button>
                    ))
                  ) : (
                    <>
                      <button
                        onClick={() => handleHitlAction(item.id, 'approve')}
                        className="btn-hitl-approve"
                      >
                        ✅ Approve
                      </button>
                      <button
                        onClick={() => handleHitlAction(item.id, 'deny')}
                        className="btn-hitl-deny"
                      >
                        ❌ Deny
                      </button>
                    </>
                  )}
                </div>
                
                {item.timestamp && (
                  <div className="hitl-timestamp">
                    Requested: {new Date(item.timestamp).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🎯</div>
            <h3>No Pending HITL Requests</h3>
            <p>Human-in-the-loop requests will appear here when the system needs your input to proceed.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HitlOraclePane;
