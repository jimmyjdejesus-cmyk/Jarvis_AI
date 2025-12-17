# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Tier 3: Smart Cloud Escalation

This module implements the third and final tier of the adaptive swarm system.
It makes intelligent decisions about when to escalate from local execution
to cloud resources based on scientific metrics and error amplification detection.

Features:
- Error amplification detection and threshold monitoring
- Efficiency-based escalation decisions
- Cost optimization for local vs cloud execution
- Performance benchmarking and adaptive thresholds
- Integration with existing AdaptiveMind systems
"""

import logging
import time
from typing import Dict, Any, Optional, Literal, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

EscalationDecision = Literal["escalate", "continue_local", "retry_local"]
ArchitectureType = Literal["single", "independent", "centralized", "decentralized", "hybrid"]


class EscalationReason(Enum):
    """Reasons for cloud escalation."""
    HIGH_ERROR_AMPLIFICATION = "high_error_amplification"
    LOW_EFFICIENCY = "low_efficiency"
    TASK_FAILURE = "task_failure"
    RESOURCE_CONSTRAINTS = "resource_constraints"
    COMPLEXITY_THRESHOLD = "complexity_threshold"
    COST_OPTIMIZATION = "cost_optimization"


@dataclass
class EscalationAnalysis:
    """Result of escalation decision analysis."""
    
    decision: EscalationDecision
    reason: EscalationReason
    confidence: float
    cost_estimate_local: float
    cost_estimate_cloud: float
    efficiency_threshold: float
    error_amplification_threshold: float
    recommendations: list[str]
    metadata: Dict[str, Any]


class CloudEscalationManager:
    """
    Smart Cloud Escalation Manager.
    
    Makes scientifically-informed decisions about when to escalate from
    local execution to cloud resources based on error amplification,
    efficiency metrics, and cost optimization.
    """
    
    def __init__(self):
        """Initialize the cloud escalation manager."""
        
        # Scientific thresholds from the paper
        self.escalation_thresholds = {
            "error_amplification": {
                "warning": 4.4,    # Centralized architecture limit
                "critical": 17.2,  # Independent architecture failure
                "immediate_escalate": 20.0  # Emergency escalation
            },
            "efficiency": {
                "target_single": 1.0,      # Single agent baseline
                "target_centralized": 1.809, # 80.9% improvement target
                "minimum_acceptable": 0.5,  # Below this = escalate
                "performance_degradation": 0.3  # 30% below target = escalate
            },
            "task_complexity": {
                "simple": 0.3,
                "moderate": 0.6,
                "complex": 0.8,
                "very_complex": 0.9
            }
        }
        
        # Cost estimation (simplified model)
        self.cost_model = {
            "local": {
                "base_cost_per_token": 0.0001,  # Local compute cost
                "coordination_overhead": 0.00005,  # Multi-agent overhead
                "setup_cost": 0.001  # One-time setup
            },
            "cloud": {
                "base_cost_per_token": 0.002,   # Cloud API cost (GPT-4, Claude)
                "coordination_overhead": 0.0001,  # Lower coordination cost
                "setup_cost": 0.01,  # Higher setup cost
                "reliability_bonus": 0.8  # 80% reliability improvement
            }
        }
        
        # Performance tracking
        self.performance_history = []
        self.escalation_history = []
        
        logger.info("CloudEscalationManager initialized with scientific thresholds")
    
    def should_escalate_to_cloud(
        self,
        swarm_result,
        task_complexity: float = 0.5,
        user_preference: Optional[str] = None,
        budget_constraints: Optional[Dict[str, float]] = None
    ) -> EscalationAnalysis:
        """
        Determine if task should be escalated to cloud resources.
        
        Args:
            swarm_result: Result from Tier 2 swarm execution
            task_complexity: Estimated complexity of task (0.0 to 1.0)
            user_preference: User preference ('local', 'cloud', 'auto')
            budget_constraints: Budget limitations
            
        Returns:
            EscalationAnalysis with decision and reasoning
        """
        start_time = time.time()
        
        logger.info("🔍 Analyzing escalation decision...")
        
        # Initialize analysis parameters
        decision_factors = []
        recommendations = []
        confidence = 0.5  # Start neutral
        
        # Factor 1: Error Amplification Analysis
        error_analysis = self._analyze_error_amplification(swarm_result)
        decision_factors.append(error_analysis)
        
        # Factor 2: Efficiency Analysis
        efficiency_analysis = self._analyze_efficiency(swarm_result, task_complexity)
        decision_factors.append(efficiency_analysis)
        
        # Factor 3: Task Complexity Analysis
        complexity_analysis = self._analyze_task_complexity(task_complexity, swarm_result)
        decision_factors.append(complexity_analysis)
        
        # Factor 4: Cost Analysis
        cost_analysis = self._analyze_costs(swarm_result, task_complexity, budget_constraints)
        decision_factors.append(cost_analysis)
        
        # Factor 5: User Preferences
        preference_analysis = self._analyze_user_preferences(user_preference, swarm_result)
        decision_factors.append(preference_analysis)
        
        # Make final decision based on all factors
        decision, reason, confidence = self._make_escalation_decision(
            decision_factors, swarm_result, task_complexity
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            decision_factors, decision, reason
        )
        
        # Calculate cost estimates
        cost_estimate_local = cost_analysis["local_cost"]
        cost_estimate_cloud = cost_analysis["cloud_cost"]
        
        processing_time = time.time() - start_time
        
        # Create escalation analysis result
        analysis = EscalationAnalysis(
            decision=decision,
            reason=reason,
            confidence=confidence,
            cost_estimate_local=cost_estimate_local,
            cost_estimate_cloud=cost_estimate_cloud,
            efficiency_threshold=self.escalation_thresholds["efficiency"]["minimum_acceptable"],
            error_amplification_threshold=self.escalation_thresholds["error_amplification"]["warning"],
            recommendations=recommendations,
            metadata={
                "processing_time": processing_time,
                "decision_factors": decision_factors,
                "task_complexity": task_complexity,
                "user_preference": user_preference,
                "swarm_metrics": {
                    "efficiency": swarm_result.efficiency,
                    "error_amplification": swarm_result.error_amplification,
                    "architecture": swarm_result.architecture,
                    "success": swarm_result.success
                }
            }
        )
        
        # Log decision for learning
        self._log_escalation_decision(analysis, swarm_result)
        
        return analysis
    
    def _analyze_error_amplification(self, swarm_result) -> Dict[str, Any]:
        """Analyze error amplification risks."""
        error_amp = swarm_result.error_amplification
        
        analysis = {
            "factor": "error_amplification",
            "value": error_amp,
            "risk_level": "low",
            "recommendation": "continue_local",
            "weight": 0.3
        }
        
        if error_amp >= self.escalation_thresholds["error_amplification"]["immediate_escalate"]:
            analysis.update({
                "risk_level": "critical",
                "recommendation": "escalate_immediately",
                "weight": 0.9,
                "reason": f"Critical error amplification: {error_amp:.1f}x (>{self.escalation_thresholds['error_amplification']['immediate_escalate']})"
            })
        elif error_amp >= self.escalation_thresholds["error_amplification"]["critical"]:
            analysis.update({
                "risk_level": "high", 
                "recommendation": "escalate",
                "weight": 0.7,
                "reason": f"High error amplification: {error_amp:.1f}x (approaching {self.escalation_thresholds['error_amplification']['critical']} failure threshold)"
            })
        elif error_amp >= self.escalation_thresholds["error_amplification"]["warning"]:
            analysis.update({
                "risk_level": "medium",
                "recommendation": "monitor",
                "weight": 0.4,
                "reason": f"Warning-level error amplification: {error_amp:.1f}x"
            })
        else:
            analysis.update({
                "reason": f"Acceptable error amplification: {error_amp:.1f}x"
            })
        
        return analysis
    
    def _analyze_efficiency(self, swarm_result, task_complexity: float) -> Dict[str, Any]:
        """Analyze efficiency performance."""
        efficiency = swarm_result.efficiency
        architecture = swarm_result.architecture
        
        # Get target efficiency for this architecture
        if architecture == "single":
            target_efficiency = self.escalation_thresholds["efficiency"]["target_single"]
        elif architecture == "centralized":
            target_efficiency = self.escalation_thresholds["efficiency"]["target_centralized"]
        else:
            target_efficiency = 1.0  # Default target
        
        # Calculate performance gap
        performance_gap = (target_efficiency - efficiency) / target_efficiency
        efficiency_ratio = efficiency / target_efficiency
        
        analysis = {
            "factor": "efficiency",
            "value": efficiency,
            "target": target_efficiency,
            "performance_gap": performance_gap,
            "efficiency_ratio": efficiency_ratio,
            "risk_level": "low",
            "recommendation": "continue_local",
            "weight": 0.25
        }
        
        # Efficiency-based escalation logic
        if efficiency < self.escalation_thresholds["efficiency"]["minimum_acceptable"]:
            analysis.update({
                "risk_level": "high",
                "recommendation": "escalate",
                "weight": 0.6,
                "reason": f"Below minimum efficiency threshold: {efficiency:.3f} < {self.escalation_thresholds['efficiency']['minimum_acceptable']}"
            })
        elif performance_gap > self.escalation_thresholds["efficiency"]["performance_degradation"]:
            analysis.update({
                "risk_level": "medium",
                "recommendation": "monitor",
                "weight": 0.4,
                "reason": f"Significant performance gap: {performance_gap:.1%} below target"
            })
        else:
            analysis.update({
                "reason": f"Acceptable efficiency: {efficiency:.3f} ({efficiency_ratio:.1%} of target)"
            })
        
        return analysis
    
    def _analyze_task_complexity(self, task_complexity: float, swarm_result) -> Dict[str, Any]:
        """Analyze task complexity impact."""
        analysis = {
            "factor": "task_complexity",
            "value": task_complexity,
            "risk_level": "low",
            "recommendation": "continue_local",
            "weight": 0.2
        }
        
        if task_complexity >= self.escalation_thresholds["task_complexity"]["very_complex"]:
            analysis.update({
                "risk_level": "high",
                "recommendation": "escalate",
                "weight": 0.5,
                "reason": f"Very complex task (complexity: {task_complexity:.1f}) may benefit from cloud resources"
            })
        elif task_complexity >= self.escalation_thresholds["task_complexity"]["complex"]:
            analysis.update({
                "risk_level": "medium",
                "recommendation": "monitor",
                "weight": 0.3,
                "reason": f"Complex task may need cloud escalation if local performance degrades"
            })
        else:
            analysis.update({
                "reason": f"Manageable task complexity: {task_complexity:.1f}"
            })
        
        return analysis
    
    def _analyze_costs(
        self, 
        swarm_result, 
        task_complexity: float, 
        budget_constraints: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Analyze cost implications of escalation."""
        tokens_used = swarm_result.tokens_used + swarm_result.coordination_tokens
        
        # Calculate local costs
        local_cost = (
            tokens_used * self.cost_model["local"]["base_cost_per_token"] +
            swarm_result.coordination_tokens * self.cost_model["local"]["coordination_overhead"] +
            self.cost_model["local"]["setup_cost"]
        )
        
        # Calculate cloud costs
        cloud_cost = (
            tokens_used * self.cost_model["cloud"]["base_cost_per_token"] +
            swarm_result.coordination_tokens * self.cost_model["cloud"]["coordination_overhead"] +
            self.cost_model["cloud"]["setup_cost"]
        )
        
        # Adjust for reliability bonus
        reliability_factor = self.cost_model["cloud"]["reliability_bonus"]
        effective_cloud_cost = cloud_cost * reliability_factor
        
        cost_ratio = effective_cloud_cost / max(local_cost, 0.001)
        
        analysis = {
            "factor": "cost",
            "local_cost": local_cost,
            "cloud_cost": cloud_cost,
            "effective_cloud_cost": effective_cloud_cost,
            "cost_ratio": cost_ratio,
            "risk_level": "low",
            "recommendation": "continue_local",
            "weight": 0.15
        }
        
        # Cost-based escalation logic
        if budget_constraints and budget_constraints.get("max_cost", float('inf')) < effective_cloud_cost:
            analysis.update({
                "risk_level": "high",
                "recommendation": "continue_local",
                "weight": 0.8,
                "reason": f"Cloud cost (${effective_cloud_cost:.4f}) exceeds budget (${budget_constraints['max_cost']:.4f})"
            })
        elif cost_ratio > 5.0:  # Cloud is 5x more expensive
            analysis.update({
                "risk_level": "medium",
                "recommendation": "continue_local",
                "weight": 0.4,
                "reason": f"Cloud cost {cost_ratio:.1f}x higher than local (${effective_cloud_cost:.4f} vs ${local_cost:.4f})"
            })
        else:
            analysis.update({
                "reason": f"Acceptable cost difference: {cost_ratio:.1f}x (${effective_cloud_cost:.4f} cloud vs ${local_cost:.4f} local)"
            })
        
        return analysis
    
    def _analyze_user_preferences(
        self, 
        user_preference: Optional[str], 
        swarm_result
    ) -> Dict[str, Any]:
        """Analyze user preferences and constraints."""
        analysis = {
            "factor": "user_preference",
            "preference": user_preference,
            "risk_level": "low",
            "recommendation": "neutral",
            "weight": 0.1
        }
        
        if user_preference == "cloud":
            analysis.update({
                "recommendation": "escalate",
                "reason": "User explicitly requested cloud resources"
            })
        elif user_preference == "local":
            analysis.update({
                "recommendation": "continue_local", 
                "reason": "User explicitly requested local execution"
            })
        else:
            analysis.update({
                "reason": "No specific user preference, using algorithmic decision"
            })
        
        return analysis
    
    def _make_escalation_decision(
        self, 
        decision_factors: list[Dict[str, Any]], 
        swarm_result, 
        task_complexity: float
    ) -> Tuple[EscalationDecision, EscalationReason, float]:
        """Make final escalation decision based on all factors."""
        
        # Check for immediate escalation triggers
        error_factor = next(f for f in decision_factors if f["factor"] == "error_amplification")
        if error_factor["recommendation"] == "escalate_immediately":
            return "escalate", EscalationReason.HIGH_ERROR_AMPLIFICATION, 0.9
        
        # Task failure = escalate
        if not swarm_result.success:
            return "escalate", EscalationReason.TASK_FAILURE, 0.8
        
        # Calculate weighted scores for each decision
        escalate_score = 0.0
        continue_score = 0.0
        total_weight = 0.0
        
        for factor in decision_factors:
            weight = factor["weight"]
            recommendation = factor["recommendation"]
            
            if recommendation in ["escalate", "escalate_immediately"]:
                escalate_score += weight
            elif recommendation == "continue_local":
                continue_score += weight
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            escalate_normalized = escalate_score / total_weight
            continue_normalized = continue_score / total_weight
        else:
            escalate_normalized = continue_normalized = 0.5
        
        # Make decision
        confidence = max(escalate_normalized, continue_normalized)
        
        if escalate_normalized > 0.6:
            # Determine primary reason for escalation
            if error_factor["risk_level"] in ["high", "critical"]:
                reason = EscalationReason.HIGH_ERROR_AMPLIFICATION
            elif next(f for f in decision_factors if f["factor"] == "efficiency")["risk_level"] == "high":
                reason = EscalationReason.LOW_EFFICIENCY
            else:
                reason = EscalationReason.COMPLEXITY_THRESHOLD
            
            return "escalate", reason, confidence
        
        elif continue_normalized > 0.6:
            return "continue_local", EscalationReason.COST_OPTIMIZATION, confidence
        
        else:
            # Marginal case - continue with local but monitor
            return "continue_local", EscalationReason.COST_OPTIMIZATION, 0.6
    
    def _generate_recommendations(
        self, 
        decision_factors: list[Dict[str, Any]], 
        decision: EscalationDecision, 
        reason: EscalationReason
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if decision == "escalate":
            recommendations.append("🚀 Escalating to cloud resources for improved reliability")
            
            # Add reason-specific recommendations
            if reason == EscalationReason.HIGH_ERROR_AMPLIFICATION:
                recommendations.append("⚠️ Local multi-agent coordination showing high error rates")
                recommendations.append("💡 Cloud models provide better consistency and reduced error propagation")
            elif reason == EscalationReason.LOW_EFFICIENCY:
                recommendations.append("📊 Local efficiency below acceptable threshold")
                recommendations.append("☁️ Cloud resources may provide better performance for this task type")
            elif reason == EscalationReason.TASK_FAILURE:
                recommendations.append("❌ Local execution failed, attempting cloud recovery")
                recommendations.append("🔄 Cloud escalation provides fallback mechanism")
        
        elif decision == "continue_local":
            recommendations.append("✅ Continuing with local execution")
            recommendations.append("💰 Cost-effective local processing maintained")
            
            # Add optimization suggestions
            efficiency_factor = next(f for f in decision_factors if f["factor"] == "efficiency")
            if efficiency_factor.get("performance_gap", 0) > 0.2:
                recommendations.append("📈 Consider optimizing local architecture for better efficiency")
            
            error_factor = next(f for f in decision_factors if f["factor"] == "error_amplification")
            if error_factor.get("risk_level") == "medium":
                recommendations.append("👁️ Monitor error rates for potential future escalation")
        
        return recommendations
    
    def _log_escalation_decision(self, analysis: EscalationAnalysis, swarm_result):
        """Log escalation decision for learning and monitoring."""
        log_entry = {
            "timestamp": time.time(),
            "decision": analysis.decision,
            "reason": analysis.reason.value,
            "confidence": analysis.confidence,
            "swarm_architecture": swarm_result.architecture,
            "efficiency": swarm_result.efficiency,
            "error_amplification": swarm_result.error_amplification,
            "cost_local": analysis.cost_estimate_local,
            "cost_cloud": analysis.cost_estimate_cloud,
            "processing_time": analysis.metadata["processing_time"]
        }
        
        self.escalation_history.append(log_entry)
        
        # Keep only recent history
        if len(self.escalation_history) > 1000:
            self.escalation_history = self.escalation_history[-500:]
        
        logger.info(f"Escalation decision: {analysis.decision} (confidence: {analysis.confidence:.2f})")
    
    def get_escalation_explanation(self, analysis: EscalationAnalysis) -> str:
        """
        Generate human-readable explanation of escalation decision.
        
        Args:
            analysis: Escalation analysis result
            
        Returns:
            Human-readable explanation
        """
        explanation = f"""
☁️ **Cloud Escalation Decision Analysis**

**Decision: {analysis.decision.upper()}**
- **Reason:** {analysis.reason.value.replace('_', ' ').title()}
- **Confidence:** {analysis.confidence:.1%}
- **Processing Time:** {analysis.metadata['processing_time']:.2f}s

**Cost Analysis:**
- **Local Cost:** ${analysis.cost_estimate_local:.4f}
- **Cloud Cost:** ${analysis.cost_estimate_cloud:.4f}
- **Cost Ratio:** {analysis.cost_estimate_cloud/max(analysis.cost_estimate_local, 0.001):.1f}x

**Current Swarm Performance:**
- **Architecture:** {analysis.metadata['swarm_metrics']['architecture'].upper()}
- **Efficiency:** {analysis.metadata['swarm_metrics']['efficiency']:.3f}
- **Error Amplification:** {analysis.metadata['swarm_metrics']['error_amplification']:.1f}x
- **Success:** {'✅' if analysis.metadata['swarm_metrics']['success'] else '❌'}

**Thresholds:**
- **Efficiency Threshold:** {analysis.efficiency_threshold:.3f}
- **Error Amplification Threshold:** {analysis.error_amplification_threshold:.1f}x

**Recommendations:**
"""
        
        for i, rec in enumerate(analysis.recommendations, 1):
            explanation += f"{i}. {rec}\n"
        
        explanation += f"""
**Decision Factors:**
"""
        for factor in analysis.metadata["decision_factors"]:
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "⚫"}.get(
                factor["risk_level"], "⚪"
            )
            explanation += f"- {risk_emoji} **{factor['factor'].title()}:** {factor.get('reason', 'N/A')}\n"
        
        return explanation
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        if not self.escalation_history:
            return {"message": "No escalation history available"}
        
        recent_decisions = self.escalation_history[-100:]  # Last 100 decisions
        
        escalate_count = sum(1 for d in recent_decisions if d["decision"] == "escalate")
        continue_count = sum(1 for d in recent_decisions if d["decision"] == "continue_local")
        
        avg_confidence = sum(d["confidence"] for d in recent_decisions) / len(recent_decisions)
        avg_efficiency = sum(d["efficiency"] for d in recent_decisions) / len(recent_decisions)
        avg_error_amp = sum(d["error_amplification"] for d in recent_decisions) / len(recent_decisions)
        
        return {
            "total_decisions": len(recent_decisions),
            "escalation_rate": escalate_count / len(recent_decisions),
            "average_confidence": avg_confidence,
            "average_efficiency": avg_efficiency,
            "average_error_amplification": avg_error_amp,
            "cost_savings_local": sum(d["cost_cloud"] - d["cost_local"] for d in recent_decisions if d["decision"] == "continue_local")
        }


# Example usage
if __name__ == "__main__":
    from .tier2_swarm_factory_standalone import SwarmExecutionResult
    
    # Test escalation manager
    escalation_manager = CloudEscalationManager()
    
    # Test with different swarm results
    test_cases = [
        # Good local performance
        SwarmExecutionResult(
            success=True,
            output="Good result",
            tokens_used=1000,
            coordination_tokens=50,
            error_amplification=1.2,
            efficiency=1.1,
            overhead=0.1,
            architecture="centralized",
            execution_time=2.5,
            metadata={}
        ),
        # High error amplification
        SwarmExecutionResult(
            success=False,
            output="Failed task",
            tokens_used=2000,
            coordination_tokens=200,
            error_amplification=18.5,
            efficiency=0.3,
            overhead=0.8,
            architecture="independent",
            execution_time=5.0,
            metadata={}
        ),
        # Low efficiency
        SwarmExecutionResult(
            success=True,
            output="Slow result",
            tokens_used=5000,
            coordination_tokens=500,
            error_amplification=2.1,
            efficiency=0.2,
            overhead=0.9,
            architecture="centralized",
            execution_time=10.0,
            metadata={}
        )
    ]
    
    for i, result in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {result.architecture.upper()} Architecture")
        print('='*60)
        
        analysis = escalation_manager.should_escalate_to_cloud(result, task_complexity=0.7)
        print(escalation_manager.get_escalation_explanation(analysis))
        
        # Print performance stats
        stats = escalation_manager.get_performance_stats()
        print(f"\nPerformance Stats: {stats}")
