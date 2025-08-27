import React, { useState, useEffect } from 'react';
import ProjectSidebar from './components/ProjectSidebar';
import ChatPane from './components/ChatPane';
import WorkflowPane from './components/WorkflowPane';
import LogViewerPane from './components/LogViewerPane';
import HitlOraclePane from './components/HitlOraclePane';
import DeadEndShelf from './components/DeadEndShelf';
import MissionHistoryView from './components/MissionHistoryView';

import SettingsView from './components/SettingsView';
import LoginForm from './components/LoginForm';
import { getAuthToken } from './auth';

import './styles.css';

// Enhanced App component with dynamic pane management and view switching
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getAuthToken());
  const [activeView, setActiveView] = useState('galaxy'); // 'galaxy', 'crew', 'agent', 'deadend'
  const [paneLayout, setPaneLayout] = useState('default'); // 'default', 'focus', 'split'
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

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

  // Show login form when no auth token is present
  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  // Render main content based on active view
  const renderMainContent = () => {
    switch (activeView) {
      case 'galaxy':
        return (
          <div className="main-content galaxy-view">
            <div className="view-header">
              <h1>🌌 Galaxy View</h1>
              <div className="view-controls">
                {/* Add controls here */}
              </div>
            </div>
            <div className="pane-container">
              <ChatPane />
              <WorkflowPane />
            </div>
          </div>
        );
      // Other cases would go here
      default:
        return <div>Unknown View</div>;
    }
  };

  return (
    <div className={`app-container theme-dark layout-${paneLayout} ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <ProjectSidebar
        activeView={activeView}
        onViewChange={handleViewChange}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      {renderMainContent()}
    </div>
  );
}

export default App;