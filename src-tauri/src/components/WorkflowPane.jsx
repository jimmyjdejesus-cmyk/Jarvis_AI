import React, { useState, useEffect, useCallback } from 'react';
import { ReactFlowProvider } from 'reactflow';
import GalaxyVisualization from './GalaxyVisualization';
import { socket } from '../socket';

const WorkflowPane = () => {
  const [viewMode, setViewMode] = useState('galaxy'); // 'galaxy' or 'traditional'
  const [workflowStats, setWorkflowStats] = useState({
    total: 0,
    completed: 0,
    running: 0,
    pending: 0,
    failed: 0,
    dead_end: 0,
    hitl_required: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionId] = useState('default-session');
  const [connected, setConnected] = useState(false);

  // Fetch workflow statistics
  const fetchWorkflowStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/workflow/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const workflowData = await response.json();
      
      // Calculate statistics from workflow data
      if (workflowData.nodes) {
        const stats = workflowData.nodes.reduce((acc, node) => {
          acc.total++;
          acc[node.status] = (acc[node.status] || 0) + 1;
          return acc;
        }, {
          total: 0,
          completed: 0,
          running: 0,
          pending: 0,
          failed: 0,
          dead_end: 0,
          hitl_required: 0
        });
        
        setWorkflowStats(stats);
      }
      
    } catch (e) {
      console.error("Failed to fetch workflow stats:", e);
      setError("Backend not connected. Using sample galaxy for demonstration.");
      
      // Generate sample stats for demo
      setWorkflowStats({
        total: 12,
        completed: 4,
        running: 3,
        pending: 2,
        failed: 1,
        dead_end: 1,
        hitl_required: 1
      });
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Initial data fetch
  useEffect(() => {
    fetchWorkflowStats();
  }, [fetchWorkflowStats]);

  // WebSocket connection status
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

  // WebSocket listeners for real-time updates
  useEffect(() => {
    const handleWorkflowUpdate = (data) => {
      console.log('Workflow update received:', data);
      
      if (data.nodes) {
        // Update statistics
        const stats = data.nodes.reduce((acc, node) => {
          acc.total++;
          acc[node.status] = (acc[node.status] || 0) + 1;
          return acc;
        }, {
          total: 0,
          completed: 0,
          running: 0,
          pending: 0,
          failed: 0,
          dead_end: 0,
          hitl_required: 0
        });
        
        setWorkflowStats(stats);
      }
    };

    const handleTaskProgress = (data) => {
      console.log('Task progress update:', data);
      // Update individual task status
      fetchWorkflowStats();
    };

    socket.on('workflow_updated', handleWorkflowUpdate);
    socket.on('task_progress', handleTaskProgress);
    socket.on('galaxy_update', handleWorkflowUpdate);
    
    return () => {
      socket.off('workflow_updated', handleWorkflowUpdate);
      socket.off('task_progress', handleTaskProgress);
      socket.off('galaxy_update', handleWorkflowUpdate);
    };
  }, [fetchWorkflowStats]);

  // Simulate workflow execution
  const simulateWorkflow = useCallback(async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/workflow/${sessionId}/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log('Workflow simulation started');
    } catch (e) {
      console.error("Failed to start workflow simulation:", e);
      
      // Simulate local updates for demo
      setTimeout(() => {
        setWorkflowStats(prev => ({
          ...prev,
          running: prev.running + 1,
          pending: Math.max(0, prev.pending - 1)
        }));
      }, 1000);
      
      setTimeout(() => {
        setWorkflowStats(prev => ({
          ...prev,
          completed: prev.completed + 1,
          running: Math.max(0, prev.running - 1)
        }));
      }, 3000);
    }
  }, [sessionId]);

  return (
    <div className="pane workflow-pane">
      <div className="pane-header">
        <h2>🧠 Cerebro Galaxy</h2>
        <div className="workflow-controls">
          <div className="view-mode-toggle">
            <button
              className={viewMode === 'galaxy' ? 'active' : ''}
              onClick={() => setViewMode('galaxy')}
            >
              🌌 Galaxy
            </button>
            <button 
              className={viewMode === 'traditional' ? 'active' : ''}
              onClick={() => setViewMode('traditional')}
            >
              📊 Traditional
            </button>
          </div>
          
          <span
            className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}
            title={connected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'}
          />
          
          <button onClick={fetchWorkflowStats} disabled={loading} className="btn-refresh">
            {loading ? '⟳' : '🔄'} Refresh
          </button>
          
          <button onClick={simulateWorkflow} className="btn-simulate">
            ⚡ Simulate
          </button>
        </div>
      </div>

      {/* Workflow Statistics Dashboard */}
      <div className="workflow-stats">
        <div className="stat-item">
          <span className="stat-label">Total Nodes:</span>
          <span className="stat-value">{workflowStats.total}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">✅ Completed:</span>
          <span className="stat-value">{workflowStats.completed}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">🔄 Running:</span>
          <span className="stat-value">{workflowStats.running}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">⏳ Pending:</span>
          <span className="stat-value">{workflowStats.pending}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">❌ Failed:</span>
          <span className="stat-value">{workflowStats.failed}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">💀 Dead-End:</span>
          <span className="stat-value">{workflowStats.dead_end}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">🤝 HITL:</span>
          <span className="stat-value">{workflowStats.hitl_required}</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Main Visualization Area */}
      <div className="workflow-canvas">
        {viewMode === 'galaxy' ? (
          <ReactFlowProvider>
            <GalaxyVisualization />
          </ReactFlowProvider>
        ) : (
          <div className="traditional-view">
            <div className="coming-soon">
              <h3>📊 Traditional Workflow View</h3>
              <p>Traditional linear workflow visualization coming soon...</p>
              <p>For now, enjoy the Cerebro Galaxy Model! 🧠🌌</p>
              <button onClick={() => setViewMode('galaxy')} className="btn-galaxy">
                🌌 Switch to Galaxy View
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Help Information */}
      <div className="workflow-help">
        <details className="help-details">
          <summary className="help-summary">ℹ️ Cerebro Galaxy Guide</summary>
          <div className="help-content">
            <h4>🧠 Cerebro-Centric Galaxy Model</h4>
            <ul>
              <li><strong>🧠 Cerebro</strong> - Central meta-agent that processes your natural language</li>
              <li><strong>🎭 Orchestrators</strong> - Multi-agent systems spawned dynamically by Cerebro</li>
              <li><strong>🤖 Agents</strong> - Individual AI agents within orchestrators</li>
              <li><strong>⚡ Tasks</strong> - Specific executions and Monte Carlo simulations</li>
            </ul>
            <h4>🎮 How to Use</h4>
            <ul>
              <li><strong>Chat with Cerebro</strong> - Type messages to activate the central brain</li>
              <li><strong>Watch Orchestrators Spawn</strong> - See new systems created based on your needs</li>
              <li><strong>Navigate the Galaxy</strong> - Click nodes to zoom into different levels</li>
              <li><strong>Monitor Real-time</strong> - Watch live updates as agents work</li>
            </ul>
          </div>
        </details>
      </div>
    </div>
  );
};

export default WorkflowPane;
