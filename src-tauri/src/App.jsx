import React, { useState, useEffect } from 'react';
import ProjectSidebar from './components/ProjectSidebar';
import ChatPane from './components/ChatPane';
import WorkflowPane from './components/WorkflowPane';
import LogViewerPane from './components/LogViewerPane';
import HitlOraclePane from './components/HitlOraclePane';
import DeadEndShelf from './components/DeadEndShelf';
import MissionHistoryView from './components/MissionHistoryView';
import './styles.css';

// Enhanced App component with dynamic pane management and view switching
function App() {
  const [activeView, setActiveView] = useState('galaxy'); // 'galaxy', 'crew', 'agent', 'deadend'
  const [paneLayout, setPaneLayout] = useState('default'); // 'default', 'focus', 'split'
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Load layout preferences from localStorage
  useEffect(() => {
    try {
      const savedLayout = localStorage.getItem('jarvis-layout-preferences');
      if (savedLayout) {
        const preferences = JSON.parse(savedLayout);
        setActiveView(preferences.activeView || 'galaxy');
        setPaneLayout(preferences.paneLayout || 'default');
        setSidebarCollapsed(preferences.sidebarCollapsed || false);
      }
    } catch (e) {
      console.error('Failed to load layout preferences:', e);
    }
  }, []);

  // Save layout preferences to localStorage
  useEffect(() => {
    try {
      const preferences = {
        activeView,
        paneLayout,
        sidebarCollapsed
      };
      localStorage.setItem('jarvis-layout-preferences', JSON.stringify(preferences));
    } catch (e) {
      console.error('Failed to save layout preferences:', e);
    }
  }, [activeView, paneLayout, sidebarCollapsed]);

  // Handle view switching
  const handleViewChange = (view) => {
    setActiveView(view);
  };

  // Handle layout change
  const handleLayoutChange = (layout) => {
    setPaneLayout(layout);
  };

  // Render main content based on active view
  const renderMainContent = () => {
    switch (activeView) {
      case 'galaxy':
        return (
          <div className="main-content galaxy-view">
            <div className="view-header">
              <h1>🌌 Galaxy View</h1>
              <div className="view-controls">
                <button 
                  className={`layout-btn ${paneLayout === 'default' ? 'active' : ''}`}
                  onClick={() => handleLayoutChange('default')}
                  title="Default Layout"
                >
                  ⊞ Default
                </button>
                <button 
                  className={`layout-btn ${paneLayout === 'focus' ? 'active' : ''}`}
                  onClick={() => handleLayoutChange('focus')}
                  title="Focus Mode"
                >
                  ⊡ Focus
                </button>
                <button 
                  className={`layout-btn ${paneLayout === 'split' ? 'active' : ''}`}
                  onClick={() => handleLayoutChange('split')}
                  title="Split View"
                >
                  ⊟ Split
                </button>
              </div>
            </div>
            
            {paneLayout === 'focus' ? (
              <div className="focus-pane">
                <WorkflowPane />
              </div>
            ) : paneLayout === 'split' ? (
              <div className="split-panes">
                <div className="left-split">
                  <ChatPane />
                </div>
                <div className="right-split">
                  <WorkflowPane />
                </div>
              </div>
            ) : (
              <div className="default-panes">
                <div className="top-panes">
                  <ChatPane />
                  <WorkflowPane />
                </div>
                <div className="bottom-panes">
                  <LogViewerPane />
                  <HitlOraclePane />
                </div>
              </div>
            )}
          </div>
        );

      case 'crew':
        return (
          <div className="main-content crew-view">
            <div className="view-header">
              <h1>👥 Crew View</h1>
              <p>Detailed view of agent crews and their coordination</p>
            </div>
            <div className="crew-content">
              <div className="crew-panes">
                <WorkflowPane />
                <div className="crew-details">
                  <HitlOraclePane />
                </div>
              </div>
            </div>
          </div>
        );

      case 'agent':
        return (
          <div className="main-content agent-view">
            <div className="view-header">
              <h1>🤖 Agent View</h1>
              <p>Individual agent configuration and monitoring</p>
            </div>
            <div className="agent-content">
              <div className="agent-panes">
                <ChatPane />
                <LogViewerPane />
              </div>
            </div>
          </div>
        );

      case 'deadend':
        return (
          <div className="main-content deadend-view">
            <div className="view-header">
              <h1>💀 Dead-End Management</h1>
              <p>Review and manage stalled or failed tasks</p>
            </div>
            <div className="deadend-content">
              <div className="deadend-panes">
                <DeadEndShelf />
                <div className="deadend-details">
                  <LogViewerPane />
                </div>
              </div>
            </div>
          </div>
        );

      case 'history':
        return (
          <div className="main-content history-view">
            <div className="view-header">
              <h1>📜 Mission History</h1>
              <p>Inspect missions, steps, and discovered facts</p>
            </div>
            <MissionHistoryView />
          </div>
        );

      default:
        return (
          <div className="main-content">
            <div className="error-view">
              <h1>⚠️ Unknown View</h1>
              <p>The requested view "{activeView}" is not available.</p>
              <button onClick={() => handleViewChange('galaxy')}>
                Return to Galaxy View
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className={`app-container ${sidebarCollapsed ? 'sidebar-collapsed' : ''} layout-${paneLayout}`}>
      {/* Enhanced sidebar with view navigation */}
      <div className="sidebar-container">
        <div className="sidebar-header">
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {sidebarCollapsed ? '▶' : '◀'}
          </button>
          {!sidebarCollapsed && <h2>J.A.R.V.I.S.</h2>}
        </div>

        {!sidebarCollapsed && (
          <>
            {/* View Navigation */}
            <div className="view-navigation">
              <h3>Views</h3>
              <nav className="view-nav">
                <button 
                  className={`nav-btn ${activeView === 'galaxy' ? 'active' : ''}`}
                  onClick={() => handleViewChange('galaxy')}
                >
                  🌌 Galaxy
                </button>
                <button 
                  className={`nav-btn ${activeView === 'crew' ? 'active' : ''}`}
                  onClick={() => handleViewChange('crew')}
                >
                  👥 Crew
                </button>
                <button 
                  className={`nav-btn ${activeView === 'agent' ? 'active' : ''}`}
                  onClick={() => handleViewChange('agent')}
                >
                  🤖 Agent
                </button>
                <button
                  className={`nav-btn ${activeView === 'deadend' ? 'active' : ''}`}
                  onClick={() => handleViewChange('deadend')}
                >
                  💀 Dead-End
                </button>
                <button
                  className={`nav-btn ${activeView === 'history' ? 'active' : ''}`}
                  onClick={() => handleViewChange('history')}
                >
                  📜 History
                </button>
              </nav>
            </div>

            {/* Project Management */}
            <ProjectSidebar />
          </>
        )}
      </div>

      {/* Main content area with dynamic views */}
      {renderMainContent()}

      {/* Status bar */}
      <div className="status-bar">
        <div className="status-left">
          <span className="status-item">View: {activeView}</span>
          <span className="status-item">Layout: {paneLayout}</span>
        </div>
        <div className="status-right">
          <span className="status-item">
            {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;
