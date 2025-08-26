import React from 'react';
import ProjectSidebar from './components/ProjectSidebar';
import ChatPane from './components/ChatPane';
import WorkflowPane from './components/WorkflowPane';
import LogViewerPane from './components/LogViewerPane';
import HitlOraclePane from './components/HitlOraclePane';
import './styles.css';

// DEV-COMMENT: This is the root component of the application.
// It assembles the entire user interface by importing and arranging all the
// major components into the multi-pane layout defined in 'styles.css'.

function App() {
  return (
    <div className="app-container">
      {/* The sidebar for project and chat management */}
      <ProjectSidebar />

      {/* The main content area, which is split into four panes */}
      <div className="main-content">
        <div className="top-panes">
          {/* The central chat window for interacting with J.A.R.V.I.S. */}
          <ChatPane />
          {/* A dedicated pane for visualizing the workflow of agent teams */}
          <WorkflowPane />
        </div>
        <div className="bottom-panes">
          {/* A pane for displaying the agent.md logs in real-time */}
          <LogViewerPane />
          {/* A pane for showing HITL recommendations from the oracle */}
          <HitlOraclePane />
        </div>
      </div>
    </div>
  );
}

export default App;
