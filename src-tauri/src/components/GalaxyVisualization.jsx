import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Panel,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { socket } from '../socket';

// Cerebro-Centric Galaxy Model: Hyper-dimensional visualization
// Cerebro (Meta-Agent) -> Orchestrators (Dynamic Multi-Agent Systems) -> Agents -> Tasks/Simulations

const ZOOM_LEVELS = {
  CEREBRO: { min: 0.1, max: 0.4, default: 0.25 },
  ORCHESTRATOR: { min: 0.4, max: 1.2, default: 0.8 },
  AGENT: { min: 1.2, max: 2.5, default: 1.8 },
  TASK: { min: 2.5, max: 6.0, default: 3.5 }
};

// Cerebro - The central meta-agent that processes natural language and spawns orchestrators
const CerebroNode = ({ data, selected }) => (
  <div className={`cerebro-node ${selected ? 'selected' : ''} ${data.status}`}>
    <div className="cerebro-core">
      <div className="cerebro-brain">
        <div className="neural-network">
          {[...Array(12)].map((_, i) => (
            <div key={i} className={`neural-node node-${i}`} 
                 style={{ 
                   animationDelay: `${i * 0.3}s`,
                   transform: `rotate(${i * 30}deg) translateX(40px)`
                 }}>
              <div className="synapse"></div>
            </div>
          ))}
        </div>
        <div className="cerebro-center">🧠</div>
      </div>
      <div className="cerebro-label">CEREBRO</div>
      <div className="cerebro-subtitle">Meta-Agent</div>
      <div className="cerebro-stats">
        <span>Active Orchestrators: {data.orchestratorCount || 0}</span>
        <span>Total Agents: {data.totalAgents || 0}</span>
        <span>Processing: {data.activeConversations || 0} conversations</span>
      </div>
      <div className="cerebro-status">
        <span className={`status-indicator ${data.status}`}></span>
        {data.status === 'thinking' && <span className="thinking-dots">...</span>}
        {data.lastMessage && (
          <div className="last-message">"{data.lastMessage}"</div>
        )}
      </div>
    </div>
  </div>
);

// Orchestrator - Dynamic multi-agent systems spawned by Cerebro
const OrchestratorNode = ({ data, selected }) => (
  <div className={`orchestrator-node ${selected ? 'selected' : ''} ${data.status}`}>
    <div className="orchestrator-core">
      <div className="orchestrator-ring">
        <div className="orchestrator-center">🎭</div>
        <div className="agent-orbits">
          {data.agents && data.agents.slice(0, 6).map((agent, i) => (
            <div key={i} className={`agent-orbit orbit-${i}`} 
                 style={{ transform: `rotate(${i * 60}deg)` }}>
              <div className={`mini-agent status-${agent.status}`}>
                {agent.icon || '🤖'}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="orchestrator-label">{data.label}</div>
      <div className="orchestrator-purpose">{data.purpose}</div>
      <div className="orchestrator-stats">
        <span>Agents: {data.agents?.length || 0}</span>
        <span>Tasks: {data.activeTasks || 0}</span>
        <span>Spawned: {data.spawnTime}</span>
      </div>
      {data.isSpawning && (
        <div className="spawning-animation">
          <div className="spawn-particles">
            {[...Array(8)].map((_, i) => (
              <div key={i} className={`particle particle-${i}`}></div>
            ))}
          </div>
          <span className="spawn-text">Spawning...</span>
        </div>
      )}
    </div>
  </div>
);

// Agent - Individual agents within orchestrators
const AgentNode = ({ data, selected }) => (
  <div className={`agent-node ${selected ? 'selected' : ''} status-${data.status}`}>
    <div className="agent-surface">
      <div className="agent-icon">{data.icon || '🤖'}</div>
      <div className="agent-atmosphere"></div>
      {data.tasks && data.tasks.length > 0 && (
        <div className="task-satellites">
          {data.tasks.slice(0, 3).map((task, i) => (
            <div key={i} className={`task-satellite satellite-${i} status-${task.status}`}>
              <span className="satellite-icon">⚡</span>
            </div>
          ))}
          {data.tasks.length > 3 && (
            <div className="satellite-count">+{data.tasks.length - 3}</div>
          )}
        </div>
      )}
    </div>
    <div className="agent-label">{data.label}</div>
    <div className="agent-details">
      <span>Role: {data.role}</span>
      <span>Tasks: {data.tasks?.length || 0}</span>
    </div>
  </div>
);

// Task - Individual tasks/simulations
const TaskNode = ({ data, selected }) => (
  <div className={`task-node ${selected ? 'selected' : ''} status-${data.status}`}>
    <div className="task-simulation">
      <div className="monte-carlo-viz">
        {[...Array(8)].map((_, i) => (
          <div key={i} className={`simulation-point point-${i}`} 
               style={{ 
                 animationDelay: `${i * 0.2}s`,
                 opacity: data.confidence ? data.confidence * 0.1 + 0.1 : 0.5 
               }}>
            •
          </div>
        ))}
      </div>
      <div className="task-label">{data.label}</div>
      <div className="task-metrics">
        <span>Progress: {(data.progress * 100).toFixed(1)}%</span>
        <span>Confidence: {(data.confidence * 100).toFixed(1)}%</span>
      </div>
    </div>
  </div>
);

const nodeTypes = {
  cerebro: CerebroNode,
  orchestrator: OrchestratorNode,
  agent: AgentNode,
  task: TaskNode,
};

const GalaxyVisualization = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [currentLevel, setCurrentLevel] = useState('cerebro');
  const [selectedNode, setSelectedNode] = useState(null);
  const [galaxyData, setGalaxyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cerebroStatus, setCerebroStatus] = useState('idle');
  const [lastUserMessage, setLastUserMessage] = useState('');
  
  const { zoomIn, zoomOut, setViewport, getViewport } = useReactFlow();
  const navigationHistory = useRef([]);

  // Generate Cerebro-centric galaxy structure
  const generateCerebroGalaxy = useCallback((data) => {
    const galaxyNodes = [];
    const galaxyEdges = [];

    // Cerebro - The central meta-agent
    const cerebroNode = {
      id: 'cerebro',
      type: 'cerebro',
      position: { x: 0, y: 0 },
      data: {
        label: 'CEREBRO',
        status: cerebroStatus,
        orchestratorCount: data?.orchestrators?.length || 0,
        totalAgents: data?.orchestrators?.reduce((sum, orch) => sum + (orch.agents?.length || 0), 0) || 0,
        activeConversations: data?.activeConversations || 1,
        lastMessage: lastUserMessage,
        level: 'cerebro'
      }
    };
    galaxyNodes.push(cerebroNode);

    // Orchestrators - Dynamically spawned multi-agent systems
    const orchestrators = data?.orchestrators || generateSampleOrchestrators();
    
    orchestrators.forEach((orchestrator, index) => {
      const angle = (index / orchestrators.length) * 2 * Math.PI;
      const radius = 250 + (index % 2) * 50; // Varying distances for visual depth
      
      const orchestratorNode = {
        id: orchestrator.id,
        type: 'orchestrator',
        position: {
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius
        },
        data: {
          ...orchestrator,
          level: 'orchestrator',
          isSpawning: orchestrator.status === 'spawning'
        }
      };
      galaxyNodes.push(orchestratorNode);

      // Connection from Cerebro to Orchestrator
      galaxyEdges.push({
        id: `cerebro-${orchestrator.id}`,
        source: 'cerebro',
        target: orchestrator.id,
        type: 'smoothstep',
        animated: orchestrator.status === 'active',
        style: { 
          stroke: orchestrator.status === 'spawning' ? '#f59e0b' : '#4ade80', 
          strokeWidth: 3,
          strokeDasharray: orchestrator.status === 'spawning' ? '10,5' : 'none'
        }
      });

      // Agents within each orchestrator
      if (orchestrator.agents) {
        orchestrator.agents.forEach((agent, agentIndex) => {
          const agentAngle = (agentIndex / orchestrator.agents.length) * 2 * Math.PI;
          const agentRadius = 120;
          
          const agentNode = {
            id: agent.id,
            type: 'agent',
            position: {
              x: orchestratorNode.position.x + Math.cos(agentAngle) * agentRadius,
              y: orchestratorNode.position.y + Math.sin(agentAngle) * agentRadius
            },
            data: {
              ...agent,
              level: 'agent'
            }
          };
          galaxyNodes.push(agentNode);

          // Connection from Orchestrator to Agent
          galaxyEdges.push({
            id: `${orchestrator.id}-${agent.id}`,
            source: orchestrator.id,
            target: agent.id,
            type: 'smoothstep',
            style: { stroke: '#60a5fa', strokeWidth: 2 }
          });

          // Tasks for each agent
          if (agent.tasks) {
            agent.tasks.forEach((task, taskIndex) => {
              const taskAngle = (taskIndex / agent.tasks.length) * 2 * Math.PI;
              const taskRadius = 60;
              
              const taskNode = {
                id: task.id,
                type: 'task',
                position: {
                  x: agentNode.position.x + Math.cos(taskAngle) * taskRadius,
                  y: agentNode.position.y + Math.sin(taskAngle) * taskRadius
                },
                data: {
                  ...task,
                  level: 'task'
                }
              };
              galaxyNodes.push(taskNode);

              // Connection from Agent to Task
              galaxyEdges.push({
                id: `${agent.id}-${task.id}`,
                source: agent.id,
                target: task.id,
                type: 'straight',
                style: { 
                  stroke: getStatusColor(task.status), 
                  strokeWidth: 1,
                  strokeDasharray: '3,3'
                }
              });
            });
          }
        });
      }
    });

    return { nodes: galaxyNodes, edges: galaxyEdges };
  }, [cerebroStatus, lastUserMessage]);

  // Generate sample orchestrators for demonstration
  const generateSampleOrchestrators = () => [
    {
      id: 'orch-research',
      label: 'Research Orchestrator',
      purpose: 'Information gathering and analysis',
      status: 'active',
      spawnTime: '2 min ago',
      activeTasks: 3,
      agents: [
        {
          id: 'agent-researcher-1',
          label: 'Web Researcher',
          role: 'researcher',
          status: 'active',
          icon: '🔍',
          tasks: [
            { id: 'task-search-1', label: 'Web Search', status: 'running', progress: 0.7, confidence: 0.85 },
            { id: 'task-analyze-1', label: 'Content Analysis', status: 'pending', progress: 0.0, confidence: 0.0 }
          ]
        },
        {
          id: 'agent-analyst-1',
          label: 'Data Analyst',
          role: 'analyst',
          status: 'thinking',
          icon: '📊',
          tasks: [
            { id: 'task-process-1', label: 'Data Processing', status: 'running', progress: 0.4, confidence: 0.72 }
          ]
        }
      ]
    },
    {
      id: 'orch-execution',
      label: 'Execution Orchestrator',
      purpose: 'Task execution and implementation',
      status: 'spawning',
      spawnTime: 'Just now',
      activeTasks: 1,
      agents: [
        {
          id: 'agent-executor-1',
          label: 'Task Executor',
          role: 'executor',
          status: 'initializing',
          icon: '⚡',
          tasks: [
            { id: 'task-execute-1', label: 'Execute Plan', status: 'pending', progress: 0.0, confidence: 0.0 }
          ]
        }
      ]
    },
    {
      id: 'orch-validation',
      label: 'Validation Orchestrator',
      purpose: 'Quality assurance and validation',
      status: 'idle',
      spawnTime: '5 min ago',
      activeTasks: 0,
      agents: [
        {
          id: 'agent-validator-1',
          label: 'Quality Validator',
          role: 'validator',
          status: 'idle',
          icon: '✅',
          tasks: []
        }
      ]
    }
  ];

  // Get status color
  const getStatusColor = (status) => {
    const colors = {
      completed: '#22c55e',
      running: '#3b82f6',
      pending: '#8b5cf6',
      failed: '#ef4444',
      idle: '#6b7280',
      thinking: '#f59e0b',
      spawning: '#f97316'
    };
    return colors[status] || '#6b7280';
  };

  // Filter nodes based on current zoom level
  const getVisibleNodes = useCallback(() => {
    const viewport = getViewport();
    const zoom = viewport.zoom;

    if (zoom <= ZOOM_LEVELS.CEREBRO.max) {
      return nodes.filter(node => node.data.level === 'cerebro' || node.data.level === 'orchestrator');
    } else if (zoom <= ZOOM_LEVELS.ORCHESTRATOR.max) {
      return nodes.filter(node => 
        node.data.level === 'orchestrator' || 
        node.data.level === 'agent' ||
        (selectedNode && node.id.startsWith(selectedNode.id))
      );
    } else if (zoom <= ZOOM_LEVELS.AGENT.max) {
      return nodes.filter(node => 
        node.data.level === 'agent' || 
        node.data.level === 'task' ||
        (selectedNode && node.id.startsWith(selectedNode.id))
      );
    } else {
      return nodes; // Show all at task level
    }
  }, [nodes, selectedNode, getViewport]);

  // Handle node selection and navigation
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
    
    // Navigate based on node level
    if (node.data.level === 'cerebro') {
      // Zoom to show orchestrators
      setViewport({ x: 0, y: 0, zoom: ZOOM_LEVELS.ORCHESTRATOR.default }, { duration: 800 });
      setCurrentLevel('orchestrator');
    } else if (node.data.level === 'orchestrator') {
      // Zoom to show agents in this orchestrator
      setViewport({ 
        x: -node.position.x * ZOOM_LEVELS.AGENT.default + 400, 
        y: -node.position.y * ZOOM_LEVELS.AGENT.default + 300, 
        zoom: ZOOM_LEVELS.AGENT.default 
      }, { duration: 800 });
      setCurrentLevel('agent');
    } else if (node.data.level === 'agent') {
      // Zoom to show tasks
      setViewport({ 
        x: -node.position.x * ZOOM_LEVELS.TASK.default + 400, 
        y: -node.position.y * ZOOM_LEVELS.TASK.default + 300, 
        zoom: ZOOM_LEVELS.TASK.default 
      }, { duration: 800 });
      setCurrentLevel('task');
    }

    // Add to navigation history
    navigationHistory.current.push({ node, level: currentLevel, viewport: getViewport() });
  }, [currentLevel, setViewport, getViewport]);

  // Navigate back in galaxy
  const navigateBack = useCallback(() => {
    if (navigationHistory.current.length > 0) {
      const previous = navigationHistory.current.pop();
      setViewport(previous.viewport, { duration: 800 });
      setCurrentLevel(previous.level);
      setSelectedNode(previous.node);
    }
  }, [setViewport]);

  // Simulate Cerebro processing a user message
  const simulateCerebroThinking = useCallback((message) => {
    setLastUserMessage(message);
    setCerebroStatus('thinking');
    
    // Simulate thinking process
    setTimeout(() => {
      setCerebroStatus('spawning');
      
      // Simulate spawning a new orchestrator
      setTimeout(() => {
        setCerebroStatus('active');
        // Refresh galaxy to show new orchestrator
        fetchGalaxyData();
      }, 2000);
    }, 1500);
  }, []);

  // Fetch galaxy data from backend
  const fetchGalaxyData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to fetch real workflow data
      const response = await fetch('http://127.0.0.1:8000/api/workflow/default-session');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const workflowData = await response.json();
      setGalaxyData(workflowData);
      
      // Generate Cerebro galaxy structure
      const { nodes: galaxyNodes, edges: galaxyEdges } = generateCerebroGalaxy(workflowData);
      setNodes(galaxyNodes);
      setEdges(galaxyEdges);
      
    } catch (e) {
      console.error("Failed to fetch galaxy data:", e);
      setError("Connected to sample galaxy. Backend integration in progress...");
      
      // Generate sample galaxy data
      const { nodes: galaxyNodes, edges: galaxyEdges } = generateCerebroGalaxy();
      setNodes(galaxyNodes);
      setEdges(galaxyEdges);
      
    } finally {
      setLoading(false);
    }
  }, [generateCerebroGalaxy, setNodes, setEdges]);

  // Initial load
  useEffect(() => {
    fetchGalaxyData();
  }, [fetchGalaxyData]);

  // WebSocket updates for real-time Cerebro integration
  useEffect(() => {
    const handleWorkflowUpdate = (data) => {
      console.log('Galaxy workflow update:', data);
      const { nodes: updatedNodes, edges: updatedEdges } = generateCerebroGalaxy(data);
      setNodes(updatedNodes);
      setEdges(updatedEdges);
    };

    const handleChatMessage = (data) => {
      console.log('Chat message received:', data);
      if (data.type === 'user' && data.message) {
        simulateCerebroThinking(data.message);
      }
    };

    const handleCerebroThinking = (data) => {
      console.log('🧠 Cerebro thinking:', data);
      setLastUserMessage(data.data?.message || '');
      setCerebroStatus('thinking');
    };

    const handleCerebroResponse = (data) => {
      console.log('🧠 Cerebro response:', data);
      setCerebroStatus('active');
      
      // Update galaxy with real orchestrator data
      if (data.data?.specialists_used?.length > 0) {
        // Refresh galaxy to show new orchestrators
        fetchGalaxyData();
      }
    };

    const handleOrchestratorSpawned = (data) => {
      console.log('🎭 Orchestrator spawned:', data);
      setCerebroStatus('spawning');
      
      // Add visual feedback for orchestrator spawning
      setTimeout(() => {
        setCerebroStatus('active');
        // Refresh galaxy to show new orchestrator
        fetchGalaxyData();
      }, 2000);
    };

    const handleAgentActivated = (data) => {
      console.log('🤖 Agent activated:', data);
      
      // Update specific agent status in real-time
      setNodes(currentNodes => 
        currentNodes.map(node => 
          node.id === data.data?.agent_id 
            ? { 
                ...node, 
                data: { 
                  ...node.data, 
                  status: 'running',
                  currentTask: data.data?.task 
                } 
              }
            : node
        )
      );
    };

    const handleChatResponse = (data) => {
      console.log('💬 Chat response from Cerebro:', data);
      
      // Update Cerebro status based on response
      if (data.data?.source === 'cerebro') {
        setCerebroStatus('active');
        
        // Show specialists involved in the response
        if (data.data?.specialists_involved?.length > 0) {
          console.log('Specialists involved:', data.data.specialists_involved);
        }
      }
    };

    // Register all event listeners
    socket.on('workflow_updated', handleWorkflowUpdate);
    socket.on('galaxy_update', handleWorkflowUpdate);
    socket.on('chat_message', handleChatMessage);
    socket.on('cerebro_thinking', handleCerebroThinking);
    socket.on('cerebro_response', handleCerebroResponse);
    socket.on('orchestrator_spawned', handleOrchestratorSpawned);
    socket.on('agent_activated', handleAgentActivated);
    socket.on('chat_response', handleChatResponse);
    
    return () => {
      socket.off('workflow_updated', handleWorkflowUpdate);
      socket.off('galaxy_update', handleWorkflowUpdate);
      socket.off('chat_message', handleChatMessage);
      socket.off('cerebro_thinking', handleCerebroThinking);
      socket.off('cerebro_response', handleCerebroResponse);
      socket.off('orchestrator_spawned', handleOrchestratorSpawned);
      socket.off('agent_activated', handleAgentActivated);
      socket.off('chat_response', handleChatResponse);
    };
  }, [generateCerebroGalaxy, setNodes, setEdges, simulateCerebroThinking, fetchGalaxyData]);

  const visibleNodes = getVisibleNodes();

  return (
    <div className="galaxy-visualization">
      <div className="galaxy-controls">
        <div className="navigation-controls">
          <button onClick={navigateBack} disabled={navigationHistory.current.length === 0}>
            ← Back
          </button>
          <span className="current-level">Level: {currentLevel}</span>
          {selectedNode && (
            <span className="selected-info">
              Selected: {selectedNode.data.label}
            </span>
          )}
        </div>
        
        <div className="zoom-controls">
          <button onClick={() => zoomOut()}>🔍-</button>
          <button onClick={() => zoomIn()}>🔍+</button>
          <button onClick={() => setViewport({ x: 0, y: 0, zoom: ZOOM_LEVELS.CEREBRO.default })}>
            🧠 Cerebro
          </button>
        </div>

        <div className="cerebro-status-display">
          <span className={`cerebro-indicator ${cerebroStatus}`}>
            🧠 Cerebro: {cerebroStatus}
          </span>
          {lastUserMessage && (
            <span className="last-message-display">
              Last: "{lastUserMessage.substring(0, 30)}..."
            </span>
          )}
        </div>
      </div>

      {loading && (
        <div className="galaxy-loading">
          <div className="loading-spinner">⟳</div>
          <span>Initializing Cerebro Galaxy...</span>
        </div>
      )}

      {error && (
        <div className="galaxy-error">
          <span>⚠️ {error}</span>
        </div>
      )}

      <ReactFlow
        nodes={visibleNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        attributionPosition="bottom-left"
        minZoom={ZOOM_LEVELS.CEREBRO.min}
        maxZoom={ZOOM_LEVELS.TASK.max}
      >
        <Controls />
        <MiniMap 
          nodeColor={(node) => getStatusColor(node.data.status)}
          maskColor="rgba(0, 0, 0, 0.2)"
        />
        <Background variant="dots" gap={20} size={1} />
        
        <Panel position="top-right">
          <div className="galaxy-legend">
            <div className="legend-title">Cerebro Galaxy Model</div>
            <div className="legend-levels">
              <div className="legend-item">
                <span className="legend-icon">🧠</span>
                <span>Cerebro (Meta-Agent)</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">🎭</span>
                <span>Orchestrator (Multi-Agent System)</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">🤖</span>
                <span>Agent (Individual AI)</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">⚡</span>
                <span>Task (Simulation/Execution)</span>
              </div>
            </div>
            <div className="legend-description">
              <p>Cerebro processes natural language and dynamically spawns orchestrators to handle complex tasks.</p>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default GalaxyVisualization;
