"""
🚀 PHASE 5: LEARNING & ADAPTATION ENGINE

Self-improving capabilities with continuous learning, pattern recognition,
and adaptive optimization based on real-world performance.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class LearningType(Enum):
    """Types of learning mechanisms"""
    SUPERVISED = "supervised"
    REINFORCEMENT = "reinforcement"
    UNSUPERVISED = "unsupervised"
    META_LEARNING = "meta_learning"
    TRANSFER = "transfer"

class PatternType(Enum):
    """Types of patterns that can be learned"""
    WORKFLOW_SUCCESS = "workflow_success"
    AGENT_PERFORMANCE = "agent_performance"
    USER_INTERACTION = "user_interaction"
    SYSTEM_OPTIMIZATION = "system_optimization"
    ERROR_RECOVERY = "error_recovery"

@dataclass
class LearningEvent:
    """Record of a learning event"""
    event_id: str
    learning_type: LearningType
    pattern_type: PatternType
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "learning_type": self.learning_type.value,
            "pattern_type": self.pattern_type.value,
            "context": self.context,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class Pattern:
    """A learned pattern with associated data"""
    pattern_id: str
    pattern_type: PatternType
    pattern_data: Dict[str, Any]
    confidence_score: float
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def update_performance(self, success: bool):
        """Update pattern performance metrics"""
        self.usage_count += 1
        
        # Exponential moving average for success rate
        alpha = 0.1
        if self.usage_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            self.success_rate = (1 - alpha) * self.success_rate + alpha * (1.0 if success else 0.0)
        
        self.last_used = datetime.now()

class PatternRecognizer:
    """Recognizes and extracts patterns from data"""
    
    def __init__(self):
        self.pattern_extractors = {
            PatternType.WORKFLOW_SUCCESS: self._extract_workflow_patterns,
            PatternType.AGENT_PERFORMANCE: self._extract_agent_patterns,
            PatternType.USER_INTERACTION: self._extract_interaction_patterns,
            PatternType.SYSTEM_OPTIMIZATION: self._extract_optimization_patterns,
            PatternType.ERROR_RECOVERY: self._extract_error_patterns
        }
    
    async def recognize_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Recognize patterns from learning events"""
        patterns = []
        
        # Group events by pattern type
        grouped_events = defaultdict(list)
        for event in events:
            grouped_events[event.pattern_type].append(event)
        
        # Extract patterns for each type
        for pattern_type, type_events in grouped_events.items():
            if pattern_type in self.pattern_extractors:
                type_patterns = await self.pattern_extractors[pattern_type](type_events)
                patterns.extend(type_patterns)
        
        return patterns
    
    async def _extract_workflow_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Extract workflow success patterns"""
        patterns = []
        
        # Find successful workflow configurations
        successful_configs = defaultdict(list)
        
        for event in events:
            if event.outcome.get("success", False):
                workflow_type = event.context.get("workflow_type", "unknown")
                config = {
                    "specialists": event.context.get("specialists", []),
                    "coordination": event.context.get("coordination_strategy", "parallel"),
                    "parameters": event.context.get("parameters", {})
                }
                successful_configs[workflow_type].append(config)
        
        # Create patterns from frequent successful configurations
        for workflow_type, configs in successful_configs.items():
            if len(configs) >= 3:  # Minimum frequency threshold
                # Find most common configuration
                config_patterns = self._find_common_configurations(configs)
                
                for pattern_data in config_patterns:
                    pattern = Pattern(
                        pattern_id=f"workflow_{workflow_type}_{len(patterns)}",
                        pattern_type=PatternType.WORKFLOW_SUCCESS,
                        pattern_data={
                            "workflow_type": workflow_type,
                            "config": pattern_data,
                            "frequency": len(configs)
                        },
                        confidence_score=min(0.95, len(configs) / 10.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _extract_agent_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Extract agent performance patterns"""
        patterns = []
        
        # Analyze agent performance correlations
        agent_performance = defaultdict(list)
        
        for event in events:
            agent_id = event.context.get("agent_id")
            if agent_id:
                performance = event.outcome.get("performance_score", 0.0)
                context_factors = {
                    "task_complexity": event.context.get("task_complexity", 0.5),
                    "resource_load": event.context.get("resource_load", 0.5),
                    "time_of_day": event.timestamp.hour
                }
                agent_performance[agent_id].append((performance, context_factors))
        
        # Find performance patterns for each agent
        for agent_id, performances in agent_performance.items():
            if len(performances) >= 5:
                optimal_conditions = self._find_optimal_conditions(performances)
                
                if optimal_conditions:
                    pattern = Pattern(
                        pattern_id=f"agent_{agent_id}_optimal",
                        pattern_type=PatternType.AGENT_PERFORMANCE,
                        pattern_data={
                            "agent_id": agent_id,
                            "optimal_conditions": optimal_conditions,
                            "sample_size": len(performances)
                        },
                        confidence_score=min(0.9, len(performances) / 20.0)
                    )
                    patterns.append(pattern)

        return patterns
    
    async def _extract_interaction_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Extract user interaction patterns"""
        patterns = []
        
        # Analyze user request patterns
        interaction_types = defaultdict(list)
        
        for event in events:
            interaction_type = event.context.get("interaction_type", "chat")
            success = event.outcome.get("success", False)
            satisfaction = event.outcome.get("user_satisfaction", 0.5)
            
            interaction_types[interaction_type].append({
                "success": success,
                "satisfaction": satisfaction,
                "context": event.context
            })
        
        # Find successful interaction patterns
        for interaction_type, interactions in interaction_types.items():
            successful_interactions = [i for i in interactions if i["success"] and i["satisfaction"] > 0.7]

            if len(successful_interactions) >= 3:
                common_factors = self._find_common_success_factors(successful_interactions)
                
                pattern = Pattern(
                    pattern_id=f"interaction_{interaction_type}_success",
                    pattern_type=PatternType.USER_INTERACTION,
                    pattern_data={
                        "interaction_type": interaction_type,
                        "success_factors": common_factors,
                        "success_rate": len(successful_interactions) / len(interactions)
                    },
                    confidence_score=min(0.85, len(successful_interactions) / 10.0)
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _extract_optimization_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Extract system optimization patterns"""
        patterns = []
        
        # Analyze optimization effectiveness
        optimizations = []
        
        for event in events:
            if "optimization" in event.context:
                optimization_data = {
                    "type": event.context.get("optimization_type"),
                    "parameters": event.context.get("optimization_parameters", {}),
                    "improvement": event.outcome.get("performance_improvement", 0.0)
                }
                optimizations.append(optimization_data)
        
        # Group by optimization type and find effective patterns
        optimization_groups = defaultdict(list)
        for opt in optimizations:
            optimization_groups[opt["type"]].append(opt)
        
        for opt_type, opts in optimization_groups.items():
            effective_opts = [o for o in opts if o["improvement"] > 0.1]
            
            if len(effective_opts) >= 2:
                avg_improvement = sum(o["improvement"] for o in effective_opts) / len(effective_opts)
                
                pattern = Pattern(
                    pattern_id=f"optimization_{opt_type}_effective",
                    pattern_type=PatternType.SYSTEM_OPTIMIZATION,
                    pattern_data={
                        "optimization_type": opt_type,
                        "average_improvement": avg_improvement,
                        "effective_count": len(effective_opts),
                        "common_parameters": self._find_common_parameters(effective_opts)
                    },
                    confidence_score=min(0.8, len(effective_opts) / 5.0)
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _extract_error_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Extract error recovery patterns"""
        patterns = []
        
        # Analyze error recovery strategies
        error_recoveries = []
        
        for event in events:
            if event.context.get("error_occurred", False):
                recovery_data = {
                    "error_type": event.context.get("error_type"),
                    "recovery_strategy": event.context.get("recovery_strategy"),
                    "recovery_success": event.outcome.get("recovery_success", False),
                    "recovery_time": event.outcome.get("recovery_time", 0.0)
                }
                error_recoveries.append(recovery_data)
        
        # Group by error type
        error_groups = defaultdict(list)
        for recovery in error_recoveries:
            error_groups[recovery["error_type"]].append(recovery)
        
        # Find effective recovery patterns
        for error_type, recoveries in error_groups.items():
            successful_recoveries = [r for r in recoveries if r["recovery_success"]]
            
            if len(successful_recoveries) >= 2:
                success_rate = len(successful_recoveries) / len(recoveries)
                avg_recovery_time = sum(r["recovery_time"] for r in successful_recoveries) / len(successful_recoveries)
                
                pattern = Pattern(
                    pattern_id=f"error_recovery_{error_type}",
                    pattern_type=PatternType.ERROR_RECOVERY,
                    pattern_data={
                        "error_type": error_type,
                        "success_rate": success_rate,
                        "average_recovery_time": avg_recovery_time,
                        "effective_strategies": [r["recovery_strategy"] for r in successful_recoveries]
                    },
                    confidence_score=success_rate
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_common_configurations(self, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find common configuration patterns"""
        # Simple implementation - find most frequent exact matches
        config_counts = defaultdict(int)
        
        for config in configs:
            config_key = json.dumps(config, sort_keys=True)
            config_counts[config_key] += 1
        
        # Return configurations that appear more than once
        common_configs = []
        for config_key, count in config_counts.items():
            if count > 1:
                common_configs.append(json.loads(config_key))
        
        return common_configs
    
    def _find_optimal_conditions(self, performances: List[Tuple[float, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """Find optimal conditions for agent performance"""
        # Find top 25% performances
        sorted_performances = sorted(performances, key=lambda x: x[0], reverse=True)
        top_25_percent = sorted_performances[:max(1, len(sorted_performances) // 4)]
        
        if len(top_25_percent) < 2:
            return None
        
        # Find common factors in top performances
        optimal_conditions = {}
        
        # For numerical factors, find ranges
        for factor in ["task_complexity", "resource_load", "time_of_day"]:
            values = [perf[1].get(factor, 0) for perf in top_25_percent if factor in perf[1]]
            if values:
                optimal_conditions[factor] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
        
        return optimal_conditions if optimal_conditions else None
    
    def _find_common_success_factors(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find common factors in successful interactions"""
        common_factors = {}
        
        # Analyze common context elements
        all_contexts = [i["context"] for i in interactions]
        
        # Find frequently occurring context keys
        key_counts = defaultdict(int)
        for context in all_contexts:
            for key in context.keys():
                key_counts[key] += 1
        
        # Include keys that appear in most interactions
        threshold = len(interactions) * 0.6
        for key, count in key_counts.items():
            if count >= threshold:
                values = [context.get(key) for context in all_contexts if key in context]
                common_factors[key] = {
                    "frequency": count / len(interactions),
                    "common_values": list(set(values))
                }
        
        return common_factors
    
    def _find_common_parameters(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find common parameters in effective optimizations"""
        all_params = []
        for opt in optimizations:
            all_params.append(opt.get("parameters", {}))
        
        common_params = {}
        if all_params:
            # Find parameters that appear in most optimizations
            param_counts = defaultdict(int)
            for params in all_params:
                for key in params.keys():
                    param_counts[key] += 1
            
            threshold = len(all_params) * 0.5
            for key, count in param_counts.items():
                if count >= threshold:
                    values = [params.get(key) for params in all_params if key in params]
                    if all(isinstance(v, (int, float)) for v in values):
                        common_params[key] = sum(values) / len(values)
                    else:
                        common_params[key] = max(set(values), key=values.count)
        
        return common_params

class AdaptationEngine:
    """Engine for adapting system behavior based on learned patterns"""
    
    def __init__(self):
        self.adaptation_strategies = {
            PatternType.WORKFLOW_SUCCESS: self._adapt_workflow_execution,
            PatternType.AGENT_PERFORMANCE: self._adapt_agent_behavior,
            PatternType.USER_INTERACTION: self._adapt_interaction_style,
            PatternType.SYSTEM_OPTIMIZATION: self._adapt_optimization_strategy,
            PatternType.ERROR_RECOVERY: self._adapt_error_handling
        }
    
    async def adapt_system(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """Adapt system behavior based on learned patterns"""
        adaptations = []
        
        for pattern in patterns:
            if pattern.confidence_score > 0.6 and pattern.pattern_type in self.adaptation_strategies:
                adaptation = await self.adaptation_strategies[pattern.pattern_type](pattern)
                if adaptation:
                    adaptations.append(adaptation)
        
        return {
            "adaptations_applied": len(adaptations),
            "adaptations": adaptations,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _adapt_workflow_execution(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Adapt workflow execution based on success patterns"""
        workflow_type = pattern.pattern_data.get("workflow_type")
        optimal_config = pattern.pattern_data.get("config")
        
        if workflow_type and optimal_config:
            return {
                "type": "workflow_optimization",
                "workflow_type": workflow_type,
                "recommended_config": optimal_config,
                "confidence": pattern.confidence_score,
                "pattern_id": pattern.pattern_id
            }
        
        return None
    
    async def _adapt_agent_behavior(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Adapt agent behavior based on performance patterns"""
        agent_id = pattern.pattern_data.get("agent_id")
        optimal_conditions = pattern.pattern_data.get("optimal_conditions")
        
        if agent_id and optimal_conditions:
            return {
                "type": "agent_optimization",
                "agent_id": agent_id,
                "optimal_conditions": optimal_conditions,
                "confidence": pattern.confidence_score,
                "pattern_id": pattern.pattern_id
            }
        
        return None
    
    async def _adapt_interaction_style(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Adapt interaction style based on user patterns"""
        interaction_type = pattern.pattern_data.get("interaction_type")
        success_factors = pattern.pattern_data.get("success_factors")
        
        if interaction_type and success_factors:
            return {
                "type": "interaction_optimization",
                "interaction_type": interaction_type,
                "success_factors": success_factors,
                "confidence": pattern.confidence_score,
                "pattern_id": pattern.pattern_id
            }
        
        return None
    
    async def _adapt_optimization_strategy(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Adapt optimization strategy based on effectiveness patterns"""
        optimization_type = pattern.pattern_data.get("optimization_type")
        common_parameters = pattern.pattern_data.get("common_parameters")
        
        if optimization_type and common_parameters:
            return {
                "type": "optimization_strategy",
                "optimization_type": optimization_type,
                "recommended_parameters": common_parameters,
                "confidence": pattern.confidence_score,
                "pattern_id": pattern.pattern_id
            }
        
        return None
    
    async def _adapt_error_handling(self, pattern: Pattern) -> Optional[Dict[str, Any]]:
        """Adapt error handling based on recovery patterns"""
        error_type = pattern.pattern_data.get("error_type")
        effective_strategies = pattern.pattern_data.get("effective_strategies")
        
        if error_type and effective_strategies:
            return {
                "type": "error_recovery",
                "error_type": error_type,
                "recommended_strategies": effective_strategies,
                "confidence": pattern.confidence_score,
                "pattern_id": pattern.pattern_id
            }
        
        return None

class LearningAdaptationEngine:
    """Main learning and adaptation engine"""
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.adaptation_engine = AdaptationEngine()
        self.learning_events: deque = deque(maxlen=10000)  # Store last 10k events
        self.learned_patterns: Dict[str, Pattern] = {}
        self.adaptations_history: List[Dict[str, Any]] = []
        
        # Learning configuration
        self.learning_interval = timedelta(hours=1)  # Learn every hour
        self.pattern_update_threshold = 10  # Update patterns after 10 new events
        self.last_learning_cycle = datetime.now()
    
    def record_learning_event(self, 
                            learning_type: LearningType,
                            pattern_type: PatternType,
                            context: Dict[str, Any],
                            outcome: Dict[str, Any],
                            confidence: float = 0.8) -> str:
        """Record a new learning event"""
        
        event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.learning_events)}"
        
        event = LearningEvent(
            event_id=event_id,
            learning_type=learning_type,
            pattern_type=pattern_type,
            context=context,
            outcome=outcome,
            confidence=confidence
        )
        
        self.learning_events.append(event)
        
        # Trigger learning if threshold reached
        if len(self.learning_events) % self.pattern_update_threshold == 0:
            asyncio.create_task(self._trigger_learning_cycle())
        
        return event_id
    
    async def _trigger_learning_cycle(self):
        """Trigger a learning and adaptation cycle"""
        try:
            logger.info("Starting learning cycle")
            
            # Learn patterns from recent events
            recent_events = list(self.learning_events)[-100:]  # Last 100 events
            new_patterns = await self.pattern_recognizer.recognize_patterns(recent_events)
            
            # Update pattern database
            for pattern in new_patterns:
                if pattern.pattern_id in self.learned_patterns:
                    # Update existing pattern
                    existing = self.learned_patterns[pattern.pattern_id]
                    existing.confidence_score = (existing.confidence_score + pattern.confidence_score) / 2
                    existing.usage_count += 1
                else:
                    # Add new pattern
                    self.learned_patterns[pattern.pattern_id] = pattern
            
            # Apply adaptations based on high-confidence patterns
            high_confidence_patterns = [
                p for p in self.learned_patterns.values() 
                if p.confidence_score > 0.7
            ]
            
            if high_confidence_patterns:
                adaptations = await self.adaptation_engine.adapt_system(high_confidence_patterns)
                self.adaptations_history.append(adaptations)
                
                logger.info(f"Applied {adaptations['adaptations_applied']} adaptations")
            
            self.last_learning_cycle = datetime.now()
            
        except Exception as e:
            logger.error(f"Learning cycle failed: {str(e)}")
    
    async def force_learning_cycle(self) -> Dict[str, Any]:
        """Force an immediate learning cycle"""
        await self._trigger_learning_cycle()
        
        return {
            "learning_cycle_completed": True,
            "patterns_learned": len(self.learned_patterns),
            "recent_adaptations": len(self.adaptations_history[-5:]) if self.adaptations_history else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status"""
        pattern_summary = defaultdict(int)
        for pattern in self.learned_patterns.values():
            pattern_summary[pattern.pattern_type.value] += 1
        
        return {
            "total_events": len(self.learning_events),
            "learned_patterns": len(self.learned_patterns),
            "pattern_breakdown": dict(pattern_summary),
            "adaptations_applied": len(self.adaptations_history),
            "last_learning_cycle": self.last_learning_cycle.isoformat(),
            "next_scheduled_cycle": (self.last_learning_cycle + self.learning_interval).isoformat()
        }
    
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights from learned patterns"""
        insights = {
            "most_successful_workflows": [],
            "optimal_agent_conditions": [],
            "effective_interactions": [],
            "best_optimizations": [],
            "reliable_error_recoveries": []
        }
        
        for pattern in self.learned_patterns.values():
            if pattern.confidence_score > 0.8:
                if pattern.pattern_type == PatternType.WORKFLOW_SUCCESS:
                    insights["most_successful_workflows"].append({
                        "workflow_type": pattern.pattern_data.get("workflow_type"),
                        "success_rate": pattern.success_rate,
                        "usage_count": pattern.usage_count
                    })
                
                elif pattern.pattern_type == PatternType.AGENT_PERFORMANCE:
                    insights["optimal_agent_conditions"].append({
                        "agent_id": pattern.pattern_data.get("agent_id"),
                        "conditions": pattern.pattern_data.get("optimal_conditions"),
                        "confidence": pattern.confidence_score
                    })
                
                # Add other pattern type insights...
        
        return insights

# Global learning engine instance
learning_engine = LearningAdaptationEngine()

# Convenience functions
def record_workflow_learning(workflow_type: str, 
                           specialists: List[str],
                           coordination_strategy: str,
                           success: bool,
                           performance_metrics: Dict[str, Any]) -> str:
    """Record workflow learning event"""
    
    return learning_engine.record_learning_event(
        learning_type=LearningType.REINFORCEMENT,
        pattern_type=PatternType.WORKFLOW_SUCCESS,
        context={
            "workflow_type": workflow_type,
            "specialists": specialists,
            "coordination_strategy": coordination_strategy,
            "timestamp": datetime.now().isoformat()
        },
        outcome={
            "success": success,
            "performance_metrics": performance_metrics
        },
        confidence=0.9 if success else 0.7
    )

def record_agent_learning(agent_id: str,
                        task_context: Dict[str, Any],
                        performance_score: float,
                        response_time: float) -> str:
    """Record agent performance learning event"""
    
    return learning_engine.record_learning_event(
        learning_type=LearningType.SUPERVISED,
        pattern_type=PatternType.AGENT_PERFORMANCE,
        context={
            "agent_id": agent_id,
            "task_complexity": task_context.get("complexity", 0.5),
            "resource_load": task_context.get("resource_load", 0.5),
            "time_of_day": datetime.now().hour
        },
        outcome={
            "performance_score": performance_score,
            "response_time": response_time
        },
        confidence=0.8
    )

async def trigger_learning() -> Dict[str, Any]:
    """Manually trigger learning cycle"""
    return await learning_engine.force_learning_cycle()

def get_learning_insights() -> Dict[str, Any]:
    """Get current learning insights"""
    return learning_engine.get_pattern_insights()
