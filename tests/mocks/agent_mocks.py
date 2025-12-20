# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Mock implementations for agents and system components.

This module provides comprehensive mock objects for agents, orchestrators,
and other system components to enable isolated testing without real
agent dependencies.
"""

import time
from enum import Enum
from unittest.mock import Mock
from typing import Dict, List, Any, Optional


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, name: str = "mock_agent", agent_type: str = "general"):
        self.name = name
        self.type = agent_type
        self.status = AgentStatus.IDLE
        self.invocation_count = 0
        self.response_history = []
        self.capabilities = []
        self.metadata = {}
        
    def invoke(self, request: str, **kwargs) -> Dict[str, Any]:
        """Mock agent invocation."""
        self.invocation_count += 1
        self.status = AgentStatus.BUSY
        
        try:
            # Generate mock response
            response = {
                "response": f"Mock response from {self.name} for: {request[:50]}...",
                "tokens_generated": len(request.split()) * 1.5,
                "avg_confidence": 0.85,
                "processing_time": 0.1,
                "agent_name": self.name,
                "timestamp": time.time()
            }
            
            self.response_history.append(response)
            self.status = AgentStatus.IDLE
            return response
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                "response": f"Error processing request: {str(e)}",
                "tokens_generated": 0,
                "avg_confidence": 0.0,
                "error": str(e)
            }
    
    def get_specialization_info(self) -> Dict[str, Any]:
        """Get agent specialization information."""
        return {
            "name": self.name,
            "type": self.type,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "invocation_count": self.invocation_count,
            "metadata": self.metadata
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform agent health check."""
        return {
            "status": self.status.value,
            "healthy": self.status != AgentStatus.ERROR,
            "last_activity": time.time(),
            "invocation_count": self.invocation_count
        }
    
    def reset(self):
        """Reset agent state."""
        self.status = AgentStatus.IDLE
        self.invocation_count = 0
        self.response_history.clear()


class MockSpecialist:
    """Mock specialist agent for testing."""
    
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.active = True
        self.performance_metrics = {
            "requests_handled": 0,
            "success_rate": 1.0,
            "avg_response_time": 0.1
        }
        
    def handle_request(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle specialist request."""
        if not self.active:
            return {"error": "Specialist is inactive"}
        
        self.performance_metrics["requests_handled"] += 1
        
        return {
            "specialist": self.name,
            "specialization": self.specialization,
            "result": f"Specialist {self.name} handled: {request}",
            "confidence": 0.9,
            "processing_time": self.performance_metrics["avg_response_time"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get specialist status."""
        return {
            "name": self.name,
            "specialization": self.specialization,
            "active": self.active,
            "metrics": self.performance_metrics
        }


class MockOrchestrator:
    """Mock orchestrator for testing."""
    
    def __init__(self):
        self.agents = {}
        self.specialists = {}
        self.active_tasks = {}
        self.task_history = []
        self.routing_rules = {}
        
    def register_agent(self, agent: MockAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
    
    def register_specialist(self, specialist: MockSpecialist):
        """Register a specialist with the orchestrator."""
        self.specialists[specialist.name] = specialist
    
    def route_request(self, request: str, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Route request to appropriate agent."""
        # Find suitable agent
        if agent_type:
            suitable_agents = [a for a in self.agents.values() if a.type == agent_type]
            if suitable_agents:
                agent = suitable_agents[0]
                return agent.invoke(request)
        
        # Default routing - use first available agent
        if self.agents:
            agent = next(iter(self.agents.values()))
            return agent.invoke(request)
        
        return {"error": "No agents available"}
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        agent_statuses = {name: agent.get_specialization_info() 
                         for name, agent in self.agents.items()}
        specialist_statuses = {name: spec.get_status() 
                              for name, spec in self.specialists.items()}
        
        return {
            "agents": agent_statuses,
            "specialists": specialist_statuses,
            "active_tasks": len(self.active_tasks),
            "total_tasks_processed": len(self.task_history)
        }
    
    def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all components."""
        results = {
            "overall_status": "healthy",
            "agents": {},
            "specialists": {},
            "timestamp": time.time()
        }
        
        # Check agents
        for name, agent in self.agents.items():
            results["agents"][name] = agent.health_check()
        
        # Check specialists
        for name, specialist in self.specialists.items():
            results["specialists"][name] = {
                "active": specialist.active,
                "status": "healthy" if specialist.active else "inactive"
            }
        
        return results


class MockMetaAgent:
    """Mock meta-agent for high-level coordination."""
    
    def __init__(self):
        self.coordination_history = []
        self.managed_agents = {}
        
    def coordinate(self, task: str, sub_tasks: List[str]) -> Dict[str, Any]:
        """Coordinate multi-agent task."""
        coordination_result = {
            "meta_agent": "MockMetaAgent",
            "main_task": task,
            "sub_tasks": sub_tasks,
            "coordination_plan": "Mock coordination strategy",
            "timestamp": time.time()
        }
        
        self.coordination_history.append(coordination_result)
        return coordination_result
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get meta-agent coordination status."""
        return {
            "coordination_history_count": len(self.coordination_history),
            "managed_agents_count": len(self.managed_agents),
            "last_coordination": self.coordination_history[-1] if self.coordination_history else None
        }


class MockWorkflowEngine:
    """Mock workflow engine for testing."""
    
    def __init__(self):
        self.workflows = {}
        self.execution_history = []
        self.active_executions = {}
        
    def create_workflow(self, name: str, steps: List[Dict]) -> str:
        """Create a new workflow."""
        workflow_id = f"workflow_{name}_{len(self.workflows)}"
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": name,
            "steps": steps,
            "created_at": time.time()
        }
        return workflow_id
    
    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        execution_id = f"exec_{workflow_id}_{len(self.execution_history)}"
        self.active_executions[execution_id] = {
            "workflow_id": workflow_id,
            "status": "running",
            "started_at": time.time(),
            "inputs": inputs
        }
        
        # Simulate execution
        result = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "completed",
            "outputs": {"result": "Mock workflow execution completed"},
            "execution_time": 0.5
        }
        
        self.execution_history.append(result)
        del self.active_executions[execution_id]
        
        return result
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        workflow = self.workflows.get(workflow_id, {})
        active_exec = [exec_id for exec_id, exec_data in self.active_executions.items() 
                      if exec_data["workflow_id"] == workflow_id]
        
        return {
            "workflow": workflow,
            "active_executions": len(active_exec),
            "total_executions": len([e for e in self.execution_history 
                                   if e["workflow_id"] == workflow_id])
        }


class MockMemoryService:
    """Mock memory service for testing."""
    
    def __init__(self):
        self.memories = {}
        self.hypergraph = Mock()
        self.vector_store = Mock()
        
    def store_memory(self, memory_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Store a memory."""
        self.memories[memory_id] = {
            "content": content,
            "metadata": metadata or {},
            "stored_at": time.time()
        }
        return True
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict]:
        """Retrieve a memory."""
        return self.memories.get(memory_id)
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memories."""
        # Mock search - return all memories for testing
        return list(self.memories.values())[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory service statistics."""
        return {
            "total_memories": len(self.memories),
            "storage_type": "mock_memory_service",
            "last_updated": max([mem["stored_at"] for mem in self.memories.values()]) if self.memories else None
        }


# Setup module-level agent mocks
def setup_agent_mocks():
    """Setup agent-related module mocks to prevent import errors."""
    import sys
    import types
    
    # Mock jarvis.agents.critics
    critics_pkg = types.ModuleType("jarvis.agents.critics")
    const_module = types.ModuleType("jarvis.agents.critics.constitutional_critic")
    
    class MockConstitutionalCritic:
        def __init__(self, *a, **k):
            pass
        
        async def review(self, *args, **kwargs):
            return {"approved": True, "feedback": ""}
    
    const_module.ConstitutionalCritic = MockConstitutionalCritic
    critics_pkg.constitutional_critic = const_module
    sys.modules.setdefault("jarvis.agents.critics", critics_pkg)
    sys.modules.setdefault("jarvis.agents.critics.constitutional_critic", const_module)
    
    # Mock specialist registry
    specialist_registry_module = types.ModuleType("jarvis.agents.specialist_registry")
    
    def get_specialist_registry():
        return {}
    
    def create_specialist(name, *args, **kwargs):
        return MockAgent(name=f"specialist:{name}")
    
    specialist_registry_module.get_specialist_registry = get_specialist_registry
    specialist_registry_module.create_specialist = create_specialist
    sys.modules.setdefault("jarvis.agents.specialist_registry", specialist_registry_module)
    
    # Mock homeostasis
    homeostasis_module = types.ModuleType("jarvis.homeostasis")
    monitor_submodule = types.ModuleType("jarvis.homeostasis.monitor")
    
    class MockSystemMonitor:
        pass
    
    monitor_submodule.SystemMonitor = MockSystemMonitor
    sys.modules.setdefault("jarvis.homeostasis", homeostasis_module)
    sys.modules.setdefault("jarvis.homeostasis.monitor", monitor_submodule)
    
    # Mock memory service
    memory_service = types.ModuleType("memory_service")
    models_sub = types.ModuleType("memory_service.models")
    hypergraph_sub = types.ModuleType("memory_service.hypergraph")
    vector_store_sub = types.ModuleType("memory_service.vector_store")
    
    class MockMetrics:
        def __init__(self, novelty=0.0, growth=0.0, cost=0.0):
            self.novelty = novelty
            self.growth = growth
            self.cost = cost
    
    class MockNegativeCheck:
        def __init__(self, *a, **k):
            pass
    
    class MockOutcome:
        def __init__(self, result="", oracle_score=0.0):
            self.result = result
            self.oracle_score = oracle_score
    
    class MockPathRecord:
        def __init__(self, *a, **k):
            pass
    
    class MockPathSignature:
        def __init__(self, *a, **k):
            pass
    
    def mock_avoid_negative(*a, **k):
        return {"avoid": False, "results": []}
    
    def mock_record_path(*a, **k):
        return None
    
    memory_service.Metrics = MockMetrics
    memory_service.NegativeCheck = MockNegativeCheck
    memory_service.Outcome = MockOutcome
    memory_service.PathRecord = MockPathRecord
    memory_service.PathSignature = MockPathSignature
    memory_service.avoid_negative = mock_avoid_negative
    memory_service.record_path = mock_record_path
    
    class MockHypergraph:
        pass
    
    class MockVectorStore:
        pass
    
    hypergraph_sub.Hypergraph = MockHypergraph
    vector_store_sub.VectorStore = MockVectorStore
    memory_service.hypergraph = hypergraph_sub
    memory_service.vector_store = vector_store_sub
    sys.modules.setdefault("memory_service", memory_service)
    sys.modules.setdefault("memory_service.models", models_sub)
    sys.modules.setdefault("memory_service.hypergraph", hypergraph_sub)
    sys.modules.setdefault("memory_service.vector_store", vector_store_sub)
    
    # Mock ecosystem
    ecosystem_pkg = types.ModuleType("jarvis.ecosystem")
    meta_module = types.ModuleType("jarvis.ecosystem.meta_intelligence")
    
    class MockExecutiveAgent:
        pass
    
    meta_module.ExecutiveAgent = MockExecutiveAgent
    ecosystem_pkg.meta_intelligence = meta_module
    ecosystem_pkg.ExecutiveAgent = MockExecutiveAgent
    ecosystem_pkg.superintelligence = types.ModuleType("jarvis.ecosystem.superintelligence")
    sys.modules.setdefault("jarvis.ecosystem", ecosystem_pkg)
    sys.modules.setdefault("jarvis.ecosystem.meta_intelligence", meta_module)
    sys.modules.setdefault("jarvis.ecosystem.superintelligence", ecosystem_pkg.superintelligence)
    
    # Mock team agents
    team_agents_module = types.ModuleType("jarvis.orchestration.team_agents")
    
    class MockBlackInnovatorAgent:
        pass
    
    team_agents_module.BlackInnovatorAgent = MockBlackInnovatorAgent
    sys.modules.setdefault("jarvis.orchestration.team_agents", team_agents_module)
    
    # Mock MCP client
    mcp_client_module = types.ModuleType("jarvis.mcp.client")
    
    class MockMCPClient:
        pass
    
    class MockModelRouter:
        pass
    
    class MockMCPServerManager:
        pass
    
    mcp_client_module.MCPClient = MockMCPClient
    mcp_client_module.ModelRouter = MockModelRouter
    mcp_client_module.MCPServerManager = MockMCPServerManager
    sys.modules.setdefault("jarvis.mcp.client", mcp_client_module)
    
    # Mock workflows
    workflows_pkg = types.ModuleType("jarvis.workflows")
    engine_module = types.ModuleType("jarvis.workflows.engine")
    
    class MockWorkflowStatus(Enum):
        PENDING = "pending"
    
    class MockWorkflowEngine:
        pass
    
    def mock_from_mission_dag(*args, **kwargs):
        return None
    
    engine_module.WorkflowStatus = MockWorkflowStatus
    engine_module.WorkflowEngine = MockWorkflowEngine
    engine_module.from_mission_dag = mock_from_mission_dag
    engine_module.workflow_engine = object()
    workflows_pkg.engine = engine_module
    sys.modules.setdefault("jarvis.workflows", workflows_pkg)
    sys.modules.setdefault("jarvis.workflows.engine", engine_module)


# Initialize agent mocks on import
setup_agent_mocks()

__all__ = [
    "AgentStatus",
    "MockAgent",
    "MockSpecialist",
    "MockOrchestrator", 
    "MockMetaAgent",
    "MockWorkflowEngine",
    "MockMemoryService",
    "setup_agent_mocks"
]
