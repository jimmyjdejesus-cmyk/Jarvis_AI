"""
🚀 PHASE 5: META-INTELLIGENCE CORE

AI managing AI systems with recursive self-improvement capabilities.
This is the brain that coordinates and evolves the entire AI ecosystem.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
from jarvis.memory import MemoryManager, ProjectMemory

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Types of AI agent capabilities"""
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    PLANNING = "planning"
    EXECUTION = "execution"
    LEARNING = "learning"
    MONITORING = "monitoring"

class SystemHealth(Enum):
    """System health status levels"""
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"

@dataclass
class AgentMetrics:
    """Performance metrics for AI agents"""
    agent_id: str
    success_rate: float = 0.0
    average_response_time: float = 0.0
    resource_usage: float = 0.0
    learning_progress: float = 0.0
    adaptation_score: float = 0.0
    reliability_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def overall_performance(self) -> float:
        """Calculate overall performance score"""
        return (
            self.success_rate * 0.3 +
            (1 - min(self.average_response_time / 10.0, 1.0)) * 0.2 +
            (1 - self.resource_usage) * 0.2 +
            self.learning_progress * 0.1 +
            self.adaptation_score * 0.1 +
            self.reliability_score * 0.1
        )

@dataclass
class SystemEvolutionPlan:
    """Plan for system evolution and improvement"""
    plan_id: str
    target_capabilities: List[AgentCapability]
    required_agents: List[str]
    optimization_targets: Dict[str, float]
    timeline: timedelta
    priority: int = 1
    status: str = "planned"
    created_at: datetime = field(default_factory=datetime.now)

class AIAgent(ABC):
    """Abstract base class for AI agents in the ecosystem"""
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.metrics = AgentMetrics(agent_id)
        self.created_at = datetime.now()
        self.is_active = True
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass
    
    @abstractmethod
    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from feedback and adapt behavior"""
        pass
    
    def update_metrics(self, success: bool, response_time: float, resource_usage: float):
        """Update agent performance metrics"""
        # Simple exponential moving average
        alpha = 0.1
        
        if success:
            self.metrics.success_rate = (1 - alpha) * self.metrics.success_rate + alpha * 1.0
        else:
            self.metrics.success_rate = (1 - alpha) * self.metrics.success_rate + alpha * 0.0
        
        self.metrics.average_response_time = (
            (1 - alpha) * self.metrics.average_response_time + alpha * response_time
        )
        
        self.metrics.resource_usage = (
            (1 - alpha) * self.metrics.resource_usage + alpha * resource_usage
        )
        
        self.metrics.last_updated = datetime.now()

class MetaAgent(AIAgent):
    """Meta-agent that manages other AI agents"""

    def __init__(self, agent_id: str, memory_manager: Optional[MemoryManager] = None):
        super().__init__(agent_id, [
            AgentCapability.REASONING,
            AgentCapability.PLANNING,
            AgentCapability.MONITORING,
            AgentCapability.LEARNING
        ])
        self.memory: MemoryManager = memory_manager or ProjectMemory()
        self.managed_agents: Dict[str, AIAgent] = {}
        self.evolution_plans: List[SystemEvolutionPlan] = []
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute meta-level coordination tasks"""
        task_type = task.get("type", "unknown")
        
        if task_type == "analyze_system":
            return await self._analyze_system_performance()
        elif task_type == "optimize_agents":
            return await self._optimize_agent_performance()
        elif task_type == "evolve_system":
            return await self._evolve_system_capabilities()
        elif task_type == "create_agent":
            return await self._create_new_agent(task)
        else:
            return {"success": False, "error": f"Unknown meta-task: {task_type}"}
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from system-wide feedback"""
        # Meta-learning: analyze patterns across all agents
        successful_patterns = feedback.get("successful_patterns", [])
        failed_patterns = feedback.get("failed_patterns", [])
        
        # Update evolution plans based on feedback
        for plan in self.evolution_plans:
            if plan.status == "executing":
                # Adjust plan based on feedback
                self._adjust_evolution_plan(plan, feedback)
        
        return True
    
    async def _analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze overall system performance"""
        analysis = {
            "total_agents": len(self.managed_agents),
            "active_agents": len([a for a in self.managed_agents.values() if a.is_active]),
            "average_performance": 0.0,
            "capability_coverage": {},
            "bottlenecks": [],
            "improvement_opportunities": []
        }
        
        if self.managed_agents:
            performances = [agent.metrics.overall_performance() for agent in self.managed_agents.values()]
            analysis["average_performance"] = sum(performances) / len(performances)
            
            # Analyze capability coverage
            for capability in AgentCapability:
                agents_with_capability = [
                    agent for agent in self.managed_agents.values()
                    if capability in agent.capabilities
                ]
                analysis["capability_coverage"][capability.value] = len(agents_with_capability)
            
            # Identify bottlenecks
            slow_agents = [
                agent for agent in self.managed_agents.values()
                if agent.metrics.average_response_time > 5.0
            ]
            analysis["bottlenecks"] = [agent.agent_id for agent in slow_agents]
            
            # Identify improvement opportunities
            low_performing_agents = [
                agent for agent in self.managed_agents.values()
                if agent.metrics.overall_performance() < 0.7
            ]
            analysis["improvement_opportunities"] = [agent.agent_id for agent in low_performing_agents]
        
        return {"success": True, "analysis": analysis}
    
    async def _optimize_agent_performance(self) -> Dict[str, Any]:
        """Optimize individual agent performance"""
        optimizations = []
        
        for agent in self.managed_agents.values():
            if agent.metrics.overall_performance() < 0.8:
                # Create optimization plan for this agent
                optimization = {
                    "agent_id": agent.agent_id,
                    "current_performance": agent.metrics.overall_performance(),
                    "optimizations": []
                }
                
                if agent.metrics.success_rate < 0.9:
                    optimization["optimizations"].append("improve_accuracy")
                
                if agent.metrics.average_response_time > 3.0:
                    optimization["optimizations"].append("reduce_latency")
                
                if agent.metrics.resource_usage > 0.8:
                    optimization["optimizations"].append("optimize_resources")
                
                optimizations.append(optimization)
        
        return {"success": True, "optimizations": optimizations}
    
    async def _evolve_system_capabilities(self) -> Dict[str, Any]:
        """Plan and execute system evolution"""
        # Analyze current capabilities vs. requirements
        current_capabilities = set()
        for agent in self.managed_agents.values():
            current_capabilities.update(agent.capabilities)
        
        all_capabilities = set(AgentCapability)
        missing_capabilities = all_capabilities - current_capabilities
        
        if missing_capabilities:
            # Create evolution plan
            plan = SystemEvolutionPlan(
                plan_id=str(uuid.uuid4()),
                target_capabilities=list(missing_capabilities),
                required_agents=[f"agent_{cap.value}" for cap in missing_capabilities],
                optimization_targets={"performance": 0.9, "efficiency": 0.8},
                timeline=timedelta(hours=1)
            )
            
            self.evolution_plans.append(plan)
            
            return {
                "success": True,
                "evolution_plan": {
                    "plan_id": plan.plan_id,
                    "missing_capabilities": [cap.value for cap in missing_capabilities],
                    "timeline": str(plan.timeline)
                }
            }
        
        return {"success": True, "message": "System capabilities are complete"}
    
    async def _create_new_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent based on requirements"""
        required_capabilities = task.get("capabilities", [])
        agent_type = task.get("agent_type", "specialist")
        
        # Create new agent (this would integrate with our existing specialist system)
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        
        # For now, create a simple specialist agent
        if required_capabilities:
            capabilities = [AgentCapability(cap) for cap in required_capabilities if cap in [c.value for c in AgentCapability]]
            new_agent = SpecialistAIAgent(agent_id, capabilities)
            self.managed_agents[agent_id] = new_agent
            
            return {
                "success": True,
                "agent_id": agent_id,
                "capabilities": [cap.value for cap in capabilities]
            }
        
        return {"success": False, "error": "No valid capabilities specified"}
    
    def _adjust_evolution_plan(self, plan: SystemEvolutionPlan, feedback: Dict[str, Any]):
        """Adjust evolution plan based on feedback"""
        success_rate = feedback.get("success_rate", 0.5)
        
        if success_rate < 0.5:
            # Plan needs adjustment
            plan.priority += 1
            plan.timeline += timedelta(hours=1)
        elif success_rate > 0.8:
            # Plan is working well
            plan.priority = max(1, plan.priority - 1)

class SpecialistAIAgent(AIAgent):
    """Specialist AI agent with specific capabilities"""
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        super().__init__(agent_id, capabilities)
        self.knowledge_base: Dict[str, Any] = {}
        self.learning_history: List[Dict[str, Any]] = []
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specialist task"""
        start_time = datetime.now()
        
        try:
            # Simulate task execution
            task_type = task.get("type", "analysis")
            
            result = {
                "success": True,
                "result": f"Completed {task_type} using capabilities: {[c.value for c in self.capabilities]}",
                "confidence": 0.85,
                "recommendations": ["Continue monitoring", "Consider optimization"]
            }
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(True, execution_time, 0.3)
            
            return result
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, execution_time, 0.5)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from task feedback"""
        self.learning_history.append({
            "timestamp": datetime.now(),
            "feedback": feedback,
            "performance_before": self.metrics.overall_performance()
        })
        
        # Simple learning: adjust behavior based on feedback
        if feedback.get("success", False):
            self.metrics.learning_progress = min(1.0, self.metrics.learning_progress + 0.1)
        else:
            # Learn from failure
            self.metrics.adaptation_score = min(1.0, self.metrics.adaptation_score + 0.05)
        
        return True

class MetaIntelligenceCore:
    """Core meta-intelligence system that manages the AI ecosystem"""
    
    def __init__(self):
        self.meta_agent = MetaAgent("meta_core")
        self.system_metrics: Dict[str, Any] = {}
        self.evolution_history: List[Dict[str, Any]] = []
        self.system_health = SystemHealth.OPTIMAL
        
        # Initialize with basic agents
        self._initialize_base_agents()
    
    def _initialize_base_agents(self):
        """Initialize the system with basic AI agents"""
        base_agents = [
            ("reasoning_agent", [AgentCapability.REASONING, AgentCapability.ANALYSIS]),
            ("creative_agent", [AgentCapability.CREATIVITY, AgentCapability.SYNTHESIS]),
            ("planning_agent", [AgentCapability.PLANNING, AgentCapability.EXECUTION]),
            ("learning_agent", [AgentCapability.LEARNING, AgentCapability.MONITORING])
        ]
        
        for agent_id, capabilities in base_agents:
            agent = SpecialistAIAgent(agent_id, capabilities)
            self.meta_agent.managed_agents[agent_id] = agent
    
    async def analyze_system_state(self) -> Dict[str, Any]:
        """Analyze the current state of the AI ecosystem"""
        analysis_task = {"type": "analyze_system"}
        analysis_result = await self.meta_agent.execute_task(analysis_task)
        
        # Update system health based on analysis
        if analysis_result.get("success", False):
            avg_performance = analysis_result["analysis"]["average_performance"]
            
            if avg_performance > 0.9:
                self.system_health = SystemHealth.OPTIMAL
            elif avg_performance > 0.8:
                self.system_health = SystemHealth.GOOD
            elif avg_performance > 0.6:
                self.system_health = SystemHealth.DEGRADED
            else:
                self.system_health = SystemHealth.CRITICAL
        
        return {
            "system_health": self.system_health.value,
            "analysis": analysis_result,
            "total_agents": len(self.meta_agent.managed_agents),
            "active_agents": len([a for a in self.meta_agent.managed_agents.values() if a.is_active])
        }
    
    async def evolve_system(self) -> Dict[str, Any]:
        """Trigger system evolution and improvement"""
        evolution_task = {"type": "evolve_system"}
        evolution_result = await self.meta_agent.execute_task(evolution_task)
        
        if evolution_result.get("success", False):
            self.evolution_history.append({
                "timestamp": datetime.now(),
                "evolution": evolution_result
            })
        
        return evolution_result
    
    async def create_specialized_agent(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new specialized agent based on requirements"""
        create_task = {
            "type": "create_agent",
            "capabilities": requirements.get("capabilities", []),
            "agent_type": requirements.get("type", "specialist")
        }
        
        return await self.meta_agent.execute_task(create_task)
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize system-wide performance"""
        optimize_task = {"type": "optimize_agents"}
        return await self.meta_agent.execute_task(optimize_task)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        for agent_id, agent in self.meta_agent.managed_agents.items():
            agent_statuses[agent_id] = {
                "performance": agent.metrics.overall_performance(),
                "success_rate": agent.metrics.success_rate,
                "response_time": agent.metrics.average_response_time,
                "capabilities": [cap.value for cap in agent.capabilities],
                "is_active": agent.is_active
            }
        
        return {
            "system_health": self.system_health.value,
            "meta_agent_performance": self.meta_agent.metrics.overall_performance(),
            "total_agents": len(self.meta_agent.managed_agents),
            "agents": agent_statuses,
            "evolution_plans": len(self.meta_agent.evolution_plans),
            "evolution_history": len(self.evolution_history)
        }
    
    async def learn_from_ecosystem_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from ecosystem-wide feedback"""
        # Meta-level learning
        await self.meta_agent.learn_from_feedback(feedback)
        
        # Distribute learning to individual agents
        for agent in self.meta_agent.managed_agents.values():
            await agent.learn_from_feedback(feedback)
        
        return True

# Global meta-intelligence instance
meta_intelligence = MetaIntelligenceCore()

# Convenience functions
async def analyze_ai_ecosystem() -> Dict[str, Any]:
    """Analyze the AI ecosystem state"""
    return await meta_intelligence.analyze_system_state()

async def evolve_ai_ecosystem() -> Dict[str, Any]:
    """Trigger AI ecosystem evolution"""
    return await meta_intelligence.evolve_system()

async def create_ai_agent(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new AI agent with specified requirements"""
    return await meta_intelligence.create_specialized_agent(requirements)

def get_ecosystem_status() -> Dict[str, Any]:
    """Get current AI ecosystem status"""
    return meta_intelligence.get_system_status()

async def create_specialist_agent(agent_id: str, capabilities: List[str], description: str = "") -> str:
    """Create a specialist agent with specific capabilities"""
    requirements = {
        "agent_id": agent_id,
        "capabilities": capabilities,
        "type": "specialist",
        "description": description
    }
    result = await meta_intelligence.create_specialized_agent(requirements)
    return result.get("agent_id", agent_id)

async def monitor_agent_ecosystem() -> Dict[str, Any]:
    """Monitor the agent ecosystem health and performance"""
    return await meta_intelligence.analyze_system_state()

def get_agent_performance() -> Dict[str, Any]:
    """Get agent performance metrics"""
    status = meta_intelligence.get_system_status()
    
    # Calculate average performance
    agents = status.get("agents", {})
    if not agents:
        return {"average_performance": 0.0, "agent_count": 0}
    
    total_performance = sum(agent.get("performance", 0.0) for agent in agents.values())
    average_performance = total_performance / len(agents)
    
    return {
        "average_performance": average_performance,
        "agent_count": len(agents),
        "system_health": status.get("system_health", "unknown"),
        "detailed_agents": agents
    }
