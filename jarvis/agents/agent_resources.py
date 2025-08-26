from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

class AgentCapability(Enum):
    REASONING = "reasoning"
    PLANNING = "planning"
    MONITORING = "monitoring"
    LEARNING = "learning"
    ANALYSIS = "analysis"
    CREATIVITY = "creativity"
    SYNTHESIS = "synthesis"
    EXECUTION = "execution"

@dataclass
class AgentMetrics:
    agent_id: str
    success_rate: float = 1.0
    average_response_time: float = 1.0
    resource_usage: float = 0.1
    last_updated: datetime = field(default_factory=datetime.now)

    def overall_performance(self) -> float:
        return self.success_rate * 0.5 + (1 - self.average_response_time / 10) * 0.3 + (1 - self.resource_usage) * 0.2

@dataclass
class SystemEvolutionPlan:
    plan_id: str
    target_capabilities: List[AgentCapability]
    required_agents: List[str]
    optimization_targets: Dict[str, float]
    timeline: datetime
    status: str = "pending"

class SystemHealth(Enum):
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
