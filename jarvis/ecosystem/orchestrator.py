"""
🚀 PHASE 5: ECOSYSTEM ORCHESTRATOR

Multi-system coordination with resource management, load balancing,
and intelligent scaling across the entire AI ecosystem.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of system resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    STORAGE = "storage"
    AI_MODELS = "ai_models"

class SystemState(Enum):
    """Overall ecosystem states"""
    OPTIMAL = "optimal"
    BALANCED = "balanced"
    STRESSED = "stressed"
    OVERLOADED = "overloaded"
    DEGRADED = "degraded"
    CRITICAL = "critical"

class ScalingAction(Enum):
    """Possible scaling actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    REDISTRIBUTE = "redistribute"
    OPTIMIZE = "optimize"
    MAINTAIN = "maintain"

@dataclass
class ResourceMetrics:
    """Resource utilization metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    network_usage: float = 0.0
    storage_usage: float = 0.0
    ai_model_load: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def overall_utilization(self) -> float:
        """Calculate overall resource utilization"""
        return (
            self.cpu_usage * 0.25 +
            self.memory_usage * 0.25 +
            self.gpu_usage * 0.20 +
            self.network_usage * 0.10 +
            self.storage_usage * 0.10 +
            self.ai_model_load * 0.10
        )
    
    def is_overloaded(self) -> bool:
        """Check if resources are overloaded"""
        return (
            self.cpu_usage > 0.9 or
            self.memory_usage > 0.9 or
            self.gpu_usage > 0.9 or
            self.overall_utilization() > 0.8
        )

@dataclass
class SystemNode:
    """Represents a node in the AI ecosystem"""
    node_id: str
    node_type: str  # "agent", "workflow_engine", "mcp_server", etc.
    capabilities: Set[str]
    resource_metrics: ResourceMetrics
    is_active: bool = True
    health_score: float = 1.0
    load_capacity: float = 1.0
    current_tasks: int = 0
    max_tasks: int = 10
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: datetime = field(default_factory=datetime.now)
    
    def can_accept_task(self) -> bool:
        """Check if node can accept more tasks"""
        return (
            self.is_active and
            self.health_score > 0.5 and
            self.current_tasks < self.max_tasks and
            not self.resource_metrics.is_overloaded()
        )
    
    def get_load_factor(self) -> float:
        """Get current load factor (0.0 to 1.0+)"""
        if self.max_tasks == 0:
            return 0.0
        return self.current_tasks / self.max_tasks

@dataclass
class TaskRequest:
    """Request for task execution"""
    task_id: str
    task_type: str
    required_capabilities: Set[str]
    priority: int = 1
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    resource_requirements: Dict[ResourceType, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    assigned_node: Optional[str] = None
    status: str = "pending"

class LoadBalancer:
    """Intelligent load balancing for task distribution"""
    
    def __init__(self):
        self.balancing_strategies = {
            "round_robin": self._round_robin_balance,
            "least_loaded": self._least_loaded_balance,
            "capability_match": self._capability_match_balance,
            "performance_weighted": self._performance_weighted_balance,
            "intelligent": self._intelligent_balance
        }
        self.last_assignment = {}
    
    async def balance_load(self, 
                         task: TaskRequest, 
                         available_nodes: List[SystemNode],
                         strategy: str = "intelligent") -> Optional[SystemNode]:
        """Balance load by selecting optimal node for task"""
        
        if strategy not in self.balancing_strategies:
            strategy = "intelligent"
        
        # Filter nodes that can handle the task
        capable_nodes = [
            node for node in available_nodes
            if (node.can_accept_task() and 
                task.required_capabilities.issubset(node.capabilities))
        ]
        
        if not capable_nodes:
            return None
        
        return await self.balancing_strategies[strategy](task, capable_nodes)
    
    async def _round_robin_balance(self, task: TaskRequest, nodes: List[SystemNode]) -> SystemNode:
        """Simple round-robin balancing"""
        task_type = task.task_type
        last_index = self.last_assignment.get(task_type, -1)
        next_index = (last_index + 1) % len(nodes)
        self.last_assignment[task_type] = next_index
        return nodes[next_index]
    
    async def _least_loaded_balance(self, task: TaskRequest, nodes: List[SystemNode]) -> SystemNode:
        """Assign to least loaded node"""
        return min(nodes, key=lambda n: n.get_load_factor())
    
    async def _capability_match_balance(self, task: TaskRequest, nodes: List[SystemNode]) -> SystemNode:
        """Assign based on capability match quality"""
        def capability_score(node: SystemNode) -> float:
            required = task.required_capabilities
            available = node.capabilities
            if not required:
                return 1.0
            
            # Score based on how well capabilities match
            overlap = len(required.intersection(available))
            extra = len(available - required)
            return (overlap / len(required)) - (extra * 0.1)  # Penalize over-qualification
        
        return max(nodes, key=capability_score)
    
    async def _performance_weighted_balance(self, task: TaskRequest, nodes: List[SystemNode]) -> SystemNode:
        """Assign based on performance and load"""
        def performance_score(node: SystemNode) -> float:
            load_penalty = node.get_load_factor()
            health_bonus = node.health_score
            resource_penalty = node.resource_metrics.overall_utilization()
            
            return health_bonus - load_penalty - (resource_penalty * 0.5)
        
        return max(nodes, key=performance_score)
    
    async def _intelligent_balance(self, task: TaskRequest, nodes: List[SystemNode]) -> SystemNode:
        """Intelligent balancing combining multiple factors"""
        def intelligent_score(node: SystemNode) -> float:
            # Capability match (40%)
            required = task.required_capabilities
            available = node.capabilities
            if required:
                capability_match = len(required.intersection(available)) / len(required)
            else:
                capability_match = 1.0
            
            # Load factor (30%)
            load_factor = 1.0 - node.get_load_factor()
            
            # Health score (20%)
            health_factor = node.health_score
            
            # Resource availability (10%)
            resource_factor = 1.0 - node.resource_metrics.overall_utilization()
            
            return (
                capability_match * 0.4 +
                load_factor * 0.3 +
                health_factor * 0.2 +
                resource_factor * 0.1
            )
        
        return max(nodes, key=intelligent_score)

class ResourceManager:
    """Manages resource allocation and optimization"""
    
    def __init__(self):
        self.resource_history: deque = deque(maxlen=1000)
        self.optimization_strategies = {
            "memory_cleanup": self._cleanup_memory,
            "cpu_optimization": self._optimize_cpu,
            "gpu_reallocation": self._reallocate_gpu,
            "task_redistribution": self._redistribute_tasks
        }
    
    async def monitor_resources(self, nodes: List[SystemNode]) -> Dict[str, Any]:
        """Monitor resource usage across all nodes"""
        total_metrics = ResourceMetrics()
        node_count = len(nodes)
        
        if node_count == 0:
            return {"status": "no_nodes", "metrics": total_metrics}
        
        # Aggregate metrics
        for node in nodes:
            total_metrics.cpu_usage += node.resource_metrics.cpu_usage
            total_metrics.memory_usage += node.resource_metrics.memory_usage
            total_metrics.gpu_usage += node.resource_metrics.gpu_usage
            total_metrics.network_usage += node.resource_metrics.network_usage
            total_metrics.storage_usage += node.resource_metrics.storage_usage
            total_metrics.ai_model_load += node.resource_metrics.ai_model_load
        
        # Calculate averages
        total_metrics.cpu_usage /= node_count
        total_metrics.memory_usage /= node_count
        total_metrics.gpu_usage /= node_count
        total_metrics.network_usage /= node_count
        total_metrics.storage_usage /= node_count
        total_metrics.ai_model_load /= node_count
        
        # Store in history
        self.resource_history.append(total_metrics)
        
        # Determine system state
        overall_utilization = total_metrics.overall_utilization()
        
        if overall_utilization < 0.3:
            state = SystemState.OPTIMAL
        elif overall_utilization < 0.5:
            state = SystemState.BALANCED
        elif overall_utilization < 0.7:
            state = SystemState.STRESSED
        elif overall_utilization < 0.9:
            state = SystemState.OVERLOADED
        else:
            state = SystemState.CRITICAL
        
        return {
            "status": "monitored",
            "system_state": state.value,
            "metrics": total_metrics,
            "node_count": node_count,
            "overloaded_nodes": len([n for n in nodes if n.resource_metrics.is_overloaded()])
        }
    
    async def optimize_resources(self, 
                               nodes: List[SystemNode], 
                               system_state: SystemState) -> Dict[str, Any]:
        """Optimize resource allocation based on system state"""
        
        if system_state in [SystemState.OPTIMAL, SystemState.BALANCED]:
            return {"status": "no_optimization_needed"}
        
        optimizations_applied = []
        
        # Apply optimizations based on system state
        if system_state == SystemState.STRESSED:
            # Light optimizations
            if await self._cleanup_memory(nodes):
                optimizations_applied.append("memory_cleanup")
        
        elif system_state == SystemState.OVERLOADED:
            # More aggressive optimizations
            if await self._cleanup_memory(nodes):
                optimizations_applied.append("memory_cleanup")
            if await self._optimize_cpu(nodes):
                optimizations_applied.append("cpu_optimization")
        
        elif system_state == SystemState.CRITICAL:
            # Emergency optimizations
            if await self._cleanup_memory(nodes):
                optimizations_applied.append("memory_cleanup")
            if await self._optimize_cpu(nodes):
                optimizations_applied.append("cpu_optimization")
            if await self._redistribute_tasks(nodes):
                optimizations_applied.append("task_redistribution")
        
        return {
            "status": "optimizations_applied",
            "optimizations": optimizations_applied,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cleanup_memory(self, nodes: List[SystemNode]) -> bool:
        """Cleanup memory across nodes"""
        # Simulate memory cleanup
        for node in nodes:
            if node.resource_metrics.memory_usage > 0.8:
                node.resource_metrics.memory_usage *= 0.9  # 10% reduction
        return True
    
    async def _optimize_cpu(self, nodes: List[SystemNode]) -> bool:
        """Optimize CPU usage"""
        # Simulate CPU optimization
        for node in nodes:
            if node.resource_metrics.cpu_usage > 0.8:
                node.resource_metrics.cpu_usage *= 0.95  # 5% reduction
        return True
    
    async def _reallocate_gpu(self, nodes: List[SystemNode]) -> bool:
        """Reallocate GPU resources"""
        # Find nodes with high GPU usage and redistribute
        high_gpu_nodes = [n for n in nodes if n.resource_metrics.gpu_usage > 0.8]
        low_gpu_nodes = [n for n in nodes if n.resource_metrics.gpu_usage < 0.3]
        
        if high_gpu_nodes and low_gpu_nodes:
            # Simulate reallocation
            for high_node in high_gpu_nodes:
                high_node.resource_metrics.gpu_usage *= 0.8
            return True
        
        return False
    
    async def _redistribute_tasks(self, nodes: List[SystemNode]) -> bool:
        """Redistribute tasks across nodes"""
        # Find overloaded and underloaded nodes
        overloaded = [n for n in nodes if n.get_load_factor() > 0.9]
        underloaded = [n for n in nodes if n.get_load_factor() < 0.3]
        
        if overloaded and underloaded:
            # Simulate task redistribution
            for overloaded_node in overloaded:
                if underloaded:
                    # Move some tasks
                    tasks_to_move = min(3, overloaded_node.current_tasks // 3)
                    overloaded_node.current_tasks -= tasks_to_move
                    underloaded[0].current_tasks += tasks_to_move
            return True
        
        return False

class EcosystemOrchestrator:
    """Main orchestrator for the AI ecosystem"""
    
    def __init__(self):
        self.nodes: Dict[str, SystemNode] = {}
        self.task_queue: deque = deque()
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: Dict[str, TaskRequest] = {}
        
        self.load_balancer = LoadBalancer()
        self.resource_manager = ResourceManager()
        
        # Orchestration settings
        self.health_check_interval = timedelta(minutes=5)
        self.resource_monitoring_interval = timedelta(minutes=1)
        self.last_health_check = datetime.now()
        self.last_resource_check = datetime.now()
        
        # Initialize with basic nodes
        self._initialize_ecosystem()
    
    def _initialize_ecosystem(self):
        """Initialize the ecosystem with basic nodes"""
        basic_nodes = [
            {
                "node_id": "workflow_engine",
                "node_type": "workflow_engine",
                "capabilities": {"workflow_execution", "task_orchestration"},
                "max_tasks": 10
            },
            {
                "node_id": "mcp_router",
                "node_type": "mcp_server", 
                "capabilities": {"model_routing", "api_management"},
                "max_tasks": 20
            },
            {
                "node_id": "specialist_coordinator",
                "node_type": "agent_coordinator",
                "capabilities": {"agent_coordination", "specialist_management"},
                "max_tasks": 15
            },
            {
                "node_id": "learning_engine",
                "node_type": "learning_system",
                "capabilities": {"pattern_recognition", "adaptation"},
                "max_tasks": 5
            }
        ]
        
        for node_config in basic_nodes:
            node = SystemNode(
                node_id=node_config["node_id"],
                node_type=node_config["node_type"],
                capabilities=set(node_config["capabilities"]),
                resource_metrics=ResourceMetrics(),
                max_tasks=node_config["max_tasks"]
            )
            self.nodes[node.node_id] = node
    
    async def submit_task(self, task: TaskRequest) -> str:
        """Submit a task for execution"""
        self.task_queue.append(task)
        
        # Try immediate assignment
        assigned_node = await self.load_balancer.balance_load(
            task, list(self.nodes.values())
        )
        
        if assigned_node:
            task.assigned_node = assigned_node.node_id
            task.status = "assigned"
            assigned_node.current_tasks += 1
            self.active_tasks[task.task_id] = task
            
            logger.info(f"Task {task.task_id} assigned to {assigned_node.node_id}")
        else:
            task.status = "queued"
            logger.info(f"Task {task.task_id} queued - no available nodes")
        
        return task.task_id
    
    async def process_task_queue(self) -> Dict[str, Any]:
        """Process pending tasks in the queue"""
        processed = 0
        assigned = 0
        
        # Process up to 10 tasks per cycle
        for _ in range(min(10, len(self.task_queue))):
            if not self.task_queue:
                break
            
            task = self.task_queue.popleft()
            processed += 1
            
            # Try to assign task
            assigned_node = await self.load_balancer.balance_load(
                task, list(self.nodes.values())
            )
            
            if assigned_node:
                task.assigned_node = assigned_node.node_id
                task.status = "assigned"
                assigned_node.current_tasks += 1
                self.active_tasks[task.task_id] = task
                assigned += 1
            else:
                # Put back in queue if no nodes available
                self.task_queue.appendleft(task)
                break
        
        return {
            "processed": processed,
            "assigned": assigned,
            "remaining_in_queue": len(self.task_queue)
        }
    
    async def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark a task as completed"""
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks.pop(task_id)
        task.status = "completed" if success else "failed"
        
        # Free up node resources
        if task.assigned_node and task.assigned_node in self.nodes:
            node = self.nodes[task.assigned_node]
            node.current_tasks = max(0, node.current_tasks - 1)
        
        self.completed_tasks[task_id] = task
        return True
    
    async def monitor_ecosystem_health(self) -> Dict[str, Any]:
        """Monitor overall ecosystem health"""
        now = datetime.now()
        
        # Health check
        if now - self.last_health_check > self.health_check_interval:
            await self._perform_health_checks()
            self.last_health_check = now
        
        # Resource monitoring
        if now - self.last_resource_check > self.resource_monitoring_interval:
            resource_status = await self.resource_manager.monitor_resources(
                list(self.nodes.values())
            )
            
            # Apply optimizations if needed
            system_state = SystemState(resource_status.get("system_state", "optimal"))
            if system_state in [SystemState.STRESSED, SystemState.OVERLOADED, SystemState.CRITICAL]:
                await self.resource_manager.optimize_resources(
                    list(self.nodes.values()), 
                    system_state
                )
            
            self.last_resource_check = now
        
        # Calculate overall health
        active_nodes = [n for n in self.nodes.values() if n.is_active]
        avg_health = sum(n.health_score for n in active_nodes) / len(active_nodes) if active_nodes else 0
        
        return {
            "ecosystem_health": avg_health,
            "active_nodes": len(active_nodes),
            "total_nodes": len(self.nodes),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "system_state": resource_status.get("system_state", "unknown") if 'resource_status' in locals() else "unknown"
        }
    
    async def _perform_health_checks(self):
        """Perform health checks on all nodes"""
        for node in self.nodes.values():
            # Simulate health check
            node.last_health_check = datetime.now()
            
            # Update health score based on resource usage and load
            load_factor = node.get_load_factor()
            resource_util = node.resource_metrics.overall_utilization()
            
            # Health decreases with high load and resource usage
            health_impact = max(0, 1.0 - (load_factor * 0.3) - (resource_util * 0.4))
            node.health_score = min(1.0, max(0.0, health_impact + 0.1))  # Min 0.1 for active nodes
            
            # Deactivate severely unhealthy nodes
            if node.health_score < 0.2:
                node.is_active = False
                logger.warning(f"Node {node.node_id} deactivated due to poor health")
            elif not node.is_active and node.health_score > 0.7:
                node.is_active = True
                logger.info(f"Node {node.node_id} reactivated - health recovered")
    
    def add_node(self, 
                node_id: str, 
                node_type: str, 
                capabilities: Set[str], 
                max_tasks: int = 10) -> bool:
        """Add a new node to the ecosystem"""
        
        if node_id in self.nodes:
            return False
        
        node = SystemNode(
            node_id=node_id,
            node_type=node_type,
            capabilities=capabilities,
            resource_metrics=ResourceMetrics(),
            max_tasks=max_tasks
        )
        
        self.nodes[node_id] = node
        logger.info(f"Added new node: {node_id} ({node_type})")
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the ecosystem"""
        
        if node_id not in self.nodes:
            return False
        
        # Reassign active tasks from this node
        node = self.nodes[node_id]
        tasks_to_reassign = [
            task for task in self.active_tasks.values() 
            if task.assigned_node == node_id
        ]
        
        for task in tasks_to_reassign:
            task.assigned_node = None
            task.status = "queued"
            self.task_queue.appendleft(task)
            self.active_tasks.pop(task.task_id, None)
        
        del self.nodes[node_id]
        logger.info(f"Removed node: {node_id}, reassigned {len(tasks_to_reassign)} tasks")
        return True
    
    def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status"""
        node_statuses = {}
        for node_id, node in self.nodes.items():
            node_statuses[node_id] = {
                "type": node.node_type,
                "active": node.is_active,
                "health": node.health_score,
                "load_factor": node.get_load_factor(),
                "current_tasks": node.current_tasks,
                "max_tasks": node.max_tasks,
                "capabilities": list(node.capabilities),
                "resource_utilization": node.resource_metrics.overall_utilization()
            }
        
        return {
            "nodes": node_statuses,
            "task_statistics": {
                "active": len(self.active_tasks),
                "queued": len(self.task_queue),
                "completed": len(self.completed_tasks)
            },
            "system_health": {
                "average_node_health": sum(n.health_score for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0,
                "active_node_ratio": len([n for n in self.nodes.values() if n.is_active]) / len(self.nodes) if self.nodes else 0
            },
            "timestamp": datetime.now().isoformat()
        }

# Global ecosystem orchestrator
ecosystem = EcosystemOrchestrator()

# Convenience functions
async def submit_ecosystem_task(task_type: str, 
                              capabilities: Set[str], 
                              priority: int = 1) -> str:
    """Submit a task to the ecosystem"""
    
    task = TaskRequest(
        task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(ecosystem.active_tasks)}",
        task_type=task_type,
        required_capabilities=capabilities,
        priority=priority
    )
    
    return await ecosystem.submit_task(task)

async def monitor_ecosystem() -> Dict[str, Any]:
    """Monitor ecosystem health and performance"""
    return await ecosystem.monitor_ecosystem_health()

def get_ecosystem_status() -> Dict[str, Any]:
    """Get current ecosystem status"""
    return ecosystem.get_ecosystem_status()

async def process_ecosystem_tasks() -> Dict[str, Any]:
    """Process pending tasks in the ecosystem"""
    return await ecosystem.process_task_queue()
