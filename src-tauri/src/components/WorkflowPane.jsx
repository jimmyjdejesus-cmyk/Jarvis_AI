import React, { useState, useEffect } from 'react';
import { http } from '@tauri-apps/api';
import Graph from 'vis-network-react';
import { socket } from '../socket';

// DEV-COMMENT: This component is responsible for visualizing the agent workflow.
// It fetches graph data (nodes and edges) from our backend API and uses the
// 'vis-network-react' library to render an interactive diagram.

const WorkflowPane = () => {
  const [graphData, setGraphData] = useState(null);
  const [error, setError] = useState(null);

  // DEV-COMMENT: The useEffect hook is used to fetch the initial workflow data
  // when the component mounts. We use Tauri's built-in http client for this,
  // which is recommended for security and performance in Tauri apps.
  useEffect(() => {
    const fetchWorkflow = async () => {
      try {
        const response = await http.fetch('http://127.0.0.1:8000/api/workflow');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        setGraphData(response.data);
      } catch (e) {
        console.error("Failed to fetch workflow:", e);
        setError("Failed to load workflow data.");
      }
    };

    fetchWorkflow();
  }, []);

  // DEV-COMMENT: Listen for real-time workflow graph updates via WebSocket.
  useEffect(() => {
    const handler = (data) => {
      setGraphData(data);
    };
    socket.on('workflow_update', handler);
    return () => socket.off('workflow_update', handler);
  }, []);

  // DEV-COMMENT: Options for configuring the appearance and behavior of the graph.
  // This allows us to define layout algorithms, node/edge styles, and interaction settings.
  const options = {
    layout: {
      hierarchical: {
        direction: "LR", // Left-to-Right layout
        sortMethod: "directed",
      },
    },
    edges: {
      color: "#84cc16",
    },
    nodes: {
        font: {
            color: "#f0f0f0",
        }
    },
    height: "100%",
    width: "100%",
  };

  return (
    <div className="pane">
      <h2>Workflow Visualization</h2>
      <div className="pane-content">
        {error && <p>{error}</p>}
        {graphData ? (
          <Graph graph={graphData} options={options} />
        ) : (
          <p>Loading workflow...</p>
        )}
      </div>
    </div>
  );
};

export default WorkflowPane;
