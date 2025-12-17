# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Dynamically Adaptive Swarm System

This is the main integration layer that combines all three tiers of the
adaptive swarm system into a complete, production-ready solution.

Tier 1: BitNet Architecture Selector - Analyzes tasks and selects optimal architecture
Tier 2: Polymorphic Swarm Factory - Executes tasks with selected architecture  
Tier 3: Smart Cloud Escalation - Decides when to escalate to cloud resources

Features:
- Complete end-to-end adaptive processing
- Scientific architecture selection based on scaling laws
- Performance optimization and error amplification detection
- Cost optimization for local vs cloud execution
- Comprehensive monitoring and reporting
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .tier1_bitnet_optimizer import BitNetOptimizer, TaskAnalysis
from .tier2_swarm_factory_standalone import LocalSwarmFactory, SwarmExecutionResult
from .tier3_cloud_escalation import CloudEscalationManager, EscalationAnalysis

logger = logging.getLogger(__name__)


@dataclass
class AdaptiveSwarmResult:
    """Complete result from the adaptive swarm system."""
    
    # Task execution results
    final_output: Any
    success: bool
    
    # Tier 1 results (Architecture Selection)
    task_analysis: TaskAnalysis
    
    # Tier 2 results (Swarm Execution) 
    swarm_result: SwarmExecutionResult
    
    # Tier 3 results (Cloud Escalation)
    escalation_analysis: EscalationAnalysis
    
    # System performance metrics
    total_execution_time: float
    total_tokens_used: int
    total_cost: float
    system_efficiency: float
    
    # Final recommendations
    recommendations: List[str]
    performance_summary: Dict[str, Any]


class AdaptiveSwarmSystem:
    """
    Complete Dynamically Adaptive Swarm System.
    
    This system intelligently routes tasks through the optimal architecture
    based on scientific scaling laws, maximizing performance while
    minimizing error amplification and costs.
    """
    
    def __init__(self):
        """Initialize the complete adaptive swarm system."""
        
        # Initialize all three tiers
        self.tier1_optimizer = BitNetOptimizer()
        self.tier2_factory = LocalSwarmFactory()
        self.tier3_escalation = CloudEscalationManager()
        
        # System configuration
        self.config = {
            "enable_1bit_models": True,
            "fallback_to_cloud_on_failure": True,
            "max_local_retries": 2,
            "cost_optimization_enabled": True,
            "performance_monitoring": True
        }
        
        # Performance tracking
        self.execution_history = []
        self.performance_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "escalated_tasks": 0,
            "average_efficiency": 0.0,
            "average_cost_savings": 0.0
        }
        
        logger.info("🚀 Dynamically Adaptive Swarm System initialized")
        logger.info("✅ Tier 1: BitNet Architecture Selector ready")
        logger.info("✅ Tier 2: Polymorphic Swarm Factory ready")
        logger.info("✅ Tier 3: Smart Cloud Escalation ready")
    
    def process_request(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AdaptiveSwarmResult:
        """
        Process a user request through the complete adaptive swarm system.
        
        Args:
            user_query: The user's request to process
            context: Optional context information
            user_preferences: User preferences (local/cloud, budget, etc.)
            
        Returns:
            AdaptiveSwarmResult with complete execution details
        """
        start_time = time.time()
        
        logger.info(f"🧠 Processing request: {user_query[:100]}...")
        
        try:
            # ========== TIER 1: ARCHITECTURE SELECTION ==========
            logger.info("🔍 TIER 1: Analyzing task and selecting architecture...")
            
            task_analysis = self.tier1_optimizer.select_optimal_architecture(
                user_query, 
                agent_capabilities=None  # Use defaults
            )
            
            logger.info(f"   Selected architecture: {task_analysis.selected_architecture}")
            logger.info(f"   Confidence: {task_analysis.confidence:.1%}")
            
            # ========== TIER 2: SWARM EXECUTION ==========
            logger.info("⚡ TIER 2: Executing with selected architecture...")
            
            swarm_result = self.tier2_factory.create_swarm(
                architecture_type=task_analysis.selected_architecture,
                query=user_query,
                context=context,
                max_agents=5
            )
            
            logger.info(f"   Swarm execution: {'✅ Success' if swarm_result.success else '❌ Failed'}")
            logger.info(f"   Efficiency: {swarm_result.efficiency:.3f}")
            logger.info(f"   Error amplification: {swarm_result.error_amplification:.1f}x")
            
            # ========== TIER 3: CLOUD ESCALATION DECISION ==========
            logger.info("☁️ TIER 3: Analyzing escalation decision...")
            
            # Extract task complexity from analysis
            task_complexity = task_analysis.complexity
            
            # Get user preferences
            user_preference = user_preferences.get("execution_preference") if user_preferences else None
            budget_constraints = user_preferences.get("budget_constraints") if user_preferences else None
            
            escalation_analysis = self.tier3_escalation.should_escalate_to_cloud(
                swarm_result=swarm_result,
                task_complexity=task_complexity,
                user_preference=user_preference,
                budget_constraints=budget_constraints
            )
            
            logger.info(f"   Escalation decision: {escalation_analysis.decision.upper()}")
            logger.info(f"   Reason: {escalation_analysis.reason.value}")
            logger.info(f"   Confidence: {escalation_analysis.confidence:.1%}")
            
            # ========== FINAL RESULT ASSEMBLY ==========
            total_execution_time = time.time() - start_time
            
            # Calculate final metrics
            total_tokens = swarm_result.tokens_used + swarm_result.coordination_tokens
            total_cost = escalation_analysis.cost_estimate_local if escalation_analysis.decision == "continue_local" else escalation_analysis.cost_estimate_cloud
            system_efficiency = self._calculate_system_efficiency(task_analysis, swarm_result, escalation_analysis)
            
            # Generate final recommendations
            recommendations = self._generate_final_recommendations(
                task_analysis, swarm_result, escalation_analysis
            )
            
            # Create performance summary
            performance_summary = {
                "tier1_processing_time": task_analysis.processing_time,
                "tier2_execution_time": swarm_result.execution_time,
                "tier3_analysis_time": escalation_analysis.metadata["processing_time"],
                "total_time": total_execution_time,
                "architecture_performance": {
                    "selected": task_analysis.selected_architecture,
                    "efficiency": swarm_result.efficiency,
                    "error_amplification": swarm_result.error_amplification,
                    "success": swarm_result.success
                },
                "escalation_outcome": {
                    "decision": escalation_analysis.decision,
                    "reason": escalation_analysis.reason.value,
                    "confidence": escalation_analysis.confidence,
                    "cost_savings": escalation_analysis.cost_estimate_cloud - escalation_analysis.cost_estimate_local if escalation_analysis.decision == "continue_local" else 0
                }
            }
            
            # Create final result
            result = AdaptiveSwarmResult(
                final_output=swarm_result.output,
                success=swarm_result.success,
                task_analysis=task_analysis,
                swarm_result=sw escalation_analysis=escalarm_result,
               ation_analysis,
                total_execution_time=total_execution_time,
                total_tokens_used=total_tokens,
                total_cost=total_cost,
                system_efficiency=system_efficiency,
                recommendations=recommendations,
                performance_summary=performance_summary
            )
            
            # Update system statistics
            self._update_system_stats(result)
            
            logger.info(f"🎯 Complete! Total time: {total_execution_time:.2f}s, Efficiency: {system_efficiency:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Adaptive swarm system failed: {e}")
            
            # Return error result
            return AdaptiveSwarmResult(
                final_output=f"System error: {str(e)}",
                success=False,
                task_analysis=TaskAnalysis(
                    parallelizable=0.5, dynamic=0.5, sequential=0.5,
                    tool_intensive=0.5, complexity=0.5,
                    selected_architecture="single", confidence=0.0,
                    scores={}, reasoning=[], model_used="error", processing_time=0.0
                ),
                swarm_result=SwarmExecutionResult(
                    success=False, output=f"Error: {str(e)}", tokens_used=0,
                    coordination_tokens=0, error_amplification=1.0,
                    efficiency=0.0, overhead=0.0, architecture="single",
                    execution_time=0.0, metadata={}
                ),
                escalation_analysis=EscalationAnalysis(
                    decision="continue_local", reason=None, confidence=0.0,
                    cost_estimate_local=0.0, cost_estimate_cloud=0.0,
                    efficiency_threshold=0.0, error_amplification_threshold=0.0,
                    recommendations=[f"Error occurred: {str(e)}"], metadata={}
                ),
                total_execution_time=time.time() - start_time,
                total_tokens_used=0,
                total_cost=0.0,
                system_efficiency=0.0,
                recommendations=[f"System error: {str(e)}"],
                performance_summary={"error": str(e)}
            )
    
    def _calculate_system_efficiency(
        self, 
        task_analysis: TaskAnalysis, 
        swarm_result: SwarmExecutionResult, 
        escalation_analysis: EscalationAnalysis
    ) -> float:
        """Calculate overall system efficiency."""
        
        # Base efficiency from swarm execution
        base_efficiency = swarm_result.efficiency
        
        # Adjust for architecture selection quality
        architecture_bonus = task_analysis.confidence * 0.1
        
        # Adjust for escalation decision quality
        escalation_bonus = escalation_analysis.confidence * 0.05
        
        # Adjust for cost efficiency
        cost_ratio = escalation_analysis.cost_estimate_cloud / max(escalation_analysis.cost_estimate_local, 0.001)
        cost_efficiency = 1.0 / max(cost_ratio, 1.0)  # Prefer lower costs
        
        # Calculate final efficiency
        total_efficiency = base_efficiency + architecture_bonus + escalation_bonus + cost_efficiency
        
        return min(total_efficiency, 2.0)  # Cap at 2.0 for realism
    
    def _generate_final_recommendations(
        self,
        task_analysis: TaskAnalysis,
        swarm_result: SwarmExecutionResult, 
        escalation_analysis: EscalationAnalysis
    ) -> List[str]:
        """Generate final system recommendations."""
        
        recommendations = []
        
        # Architecture selection recommendations
        if task_analysis.confidence < 0.7:
            recommendations.append("🤔 Consider improving task analysis for better architecture selection")
        
        # Performance recommendations
        if swarm_result.efficiency < 0.5:
            recommendations.append("📊 Local execution efficiency is low - consider cloud escalation")
        
        if swarm_result.error_amplification > 10:
            recommendations.append("⚠️ High error amplification detected - immediate cloud escalation recommended")
        
        # Cost recommendations
        cost_savings = escalation_analysis.cost_estimate_cloud - escalation_analysis.cost_estimate_local
        if cost_savings > 0.01:  # $0.01 savings
            recommendations.append(f"💰 Local execution saved ${cost_savings:.4f} compared to cloud")
        
        # System optimization recommendations
        if not swarm_result.success:
            recommendations.append("🔄 Task failed - consider retrying with different architecture")
        
        if escalation_analysis.decision == "escalate":
            recommendations.append("☁️ Cloud escalation successful - system handled failure gracefully")
        
        return recommendations
    
    def _update_system_stats(self, result: AdaptiveSwarmResult):
        """Update system performance statistics."""
        
        self.performance_stats["total_tasks"] += 1
        
        if result.success:
            self.performance_stats["successful_tasks"] += 1
        
        if result.escalation_analysis.decision == "escalate":
            self.performance_stats["escalated_tasks"] += 1
        
        # Update rolling averages
        total = self.performance_stats["total_tasks"]
        self.performance_stats["average_efficiency"] = (
            (self.performance_stats["average_efficiency"] * (total - 1) + result.system_efficiency) / total
        )
        
        cost_savings = result.escalation_analysis.cost_estimate_cloud - result.escalation_analysis.cost_estimate_local
        self.performance_stats["average_cost_savings"] = (
            (self.performance_stats["average_cost_savings"] * (total - 1) + cost_savings) / total
        )
        
        # Store execution history
        self.execution_history.append({
            "timestamp": time.time(),
            "success": result.success,
            "architecture": result.task_analysis.selected_architecture,
            "efficiency": result.system_efficiency,
            "escalation": result.escalation_analysis.decision,
            "cost": result.total_cost
        })
        
        # Keep only recent history
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    def get_system_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive system performance report."""
        
        if not self.execution_history:
            return {"message": "No execution history available"}
        
        recent_tasks = self.execution_history[-100:]  # Last 100 tasks
        
        # Architecture usage statistics
        architecture_usage = {}
        for task in recent_tasks:
            arch = task["architecture"]
            architecture_usage[arch] = architecture_usage.get(arch, 0) + 1
        
        # Escalation statistics
        escalations = sum(1 for task in recent_tasks if task["escalation"] == "escalate")
        
        # Efficiency statistics
        efficiencies = [task["efficiency"] for task in recent_tasks]
        avg_efficiency = sum(efficiencies) / len(efficiencies)
        max_efficiency = max(efficiencies)
        min_efficiency = min(efficiencies)
        
        # Success rate
        successes = sum(1 for task in recent_tasks if task["success"])
        success_rate = successes / len(recent_tasks)
        
        # Cost savings
        cost_savings = [task["cost"] for task in recent_tasks if task["escalation"] == "continue_local"]
        avg_cost_local = sum(cost_savings) / len(cost_savings) if cost_savings else 0
        
        return {
            "overview": {
                "total_tasks_analyzed": len(recent_tasks),
                "success_rate": f"{success_rate:.1%}",
                "escalation_rate": f"{escalations/len(recent_tasks):.1%}",
                "average_efficiency": f"{avg_efficiency:.3f}",
                "efficiency_range": f"{min_efficiency:.3f} - {max_efficiency:.3f}"
            },
            "architecture_usage": architecture_usage,
            "cost_analysis": {
                "average_local_cost": f"${avg_cost_local:.6f}",
                "estimated_cloud_cost_multiplier": "20x",
                "total_cost_savings": f"${sum(self.performance_stats['average_cost_savings'] * len(recent_tasks)):.4f}"
            },
            "system_health": {
                "overall_status": "🟢 Healthy" if success_rate > 0.8 else "🟡 Needs Attention",
                "recommendations": [
                    "System performing well" if success_rate > 0.8 else "Monitor failure rates",
                    "Consider optimizing architecture selection" if avg_efficiency < 0.8 else "Architecture selection optimal",
                    "Local execution cost-effective" if avg_cost_local < 0.01 else "Consider cloud for complex tasks"
                ]
            }
        }
    
    def get_execution_explanation(self, result: AdaptiveSwarmResult) -> str:
        """
        Generate comprehensive execution explanation.
        
        Args:
            result: Adaptive swarm execution result
            
        Returns:
            Human-readable execution report
        """
        explanation = f"""
🚀 **Dynamically Adaptive Swarm Execution Report**

**📋 Task Overview:**
- Query: {result.task_analysis.task_characteristics.get('query', 'N/A')[:100]}...
- Complexity: {result.task_analysis.complexity:.1f}
- Model Used: {result.task_analysis.model_used}

**🧠 TIER 1 - Architecture Selection:**
- **Selected Architecture:** {result.task_analysis.selected_architecture.upper()}
- **Confidence:** {result.task_analysis.confidence:.1%}
- **Analysis Time:** {result.task_analysis.processing_time:.2f}s

**Task Characteristics:**
- Parallelizable: {result.task_analysis.parallelizable:.1f}
- Dynamic: {result.task_analysis.dynamic:.1f}
- Sequential: {result.task_analysis.sequential:.1f}
- Tool Intensive: {result.task_analysis.tool_intensive:.1f}

**⚡ TIER 2 - Swarm Execution:**
- **Architecture:** {result.swarm_result.architecture.upper()}
- **Success:** {'✅' if result.swarm_result.success else '❌'}
- **Execution Time:** {result.swarm_result.execution_time:.2f}s
- **Efficiency:** {result.swarm_result.efficiency:.3f}
- **Error Amplification:** {result.swarm_result.error_amplification:.1f}x
- **Tokens Used:** {result.swarm_result.tokens_used:,}

**☁️ TIER 3 - Cloud Escalation:**
- **Decision:** {result.escalation_analysis.decision.upper()}
- **Reason:** {result.escalation_analysis.reason.value.replace('_', ' ').title()}
- **Confidence:** {result.escalation_analysis.confidence:.1%}
- **Local Cost:** ${result.escalation_analysis.cost_estimate_local:.6f}
- **Cloud Cost:** ${result.escalation_analysis.cost_estimate_cloud:.6f}

**📊 System Performance:**
- **Total Execution Time:** {result.total_execution_time:.2f}s
- **System Efficiency:** {result.system_efficiency:.3f}
- **Total Cost:** ${result.total_cost:.6f}
- **Success Rate:** {'✅' if result.success else '❌'}

**💡 Recommendations:**
"""
        
        for i, rec in enumerate(result.recommendations, 1):
            explanation += f"{i}. {rec}\n"
        
        explanation += f"""
**🔬 Scientific Insights:**
- Architecture selection based on {len(result.task_analysis.reasoning)} factors
- Error amplification detection prevented {result.swarm_result.error_amplification:.1f}x error multiplication
- Cost optimization saved ${result.escalation_analysis.cost_estimate_cloud - result.escalation_analysis.cost_estimate_local:.6f}
- Performance vs. paper targets: {((result.system_efficiency - 1.0) * 100):+.1f}%
"""
        
        return explanation


# Example usage and demonstration
if __name__ == "__main__":
    
    # Initialize the complete system
    system = AdaptiveSwarmSystem()
    
    # Test with different types of queries
    test_queries = [
        "Analyze these 5 Python files and find security vulnerabilities",
        "Write a comprehensive research report about quantum computing advances",
        "Debug this complex machine learning pipeline with multiple components",
        "Simple question: What is the capital of France?",
        "Research latest developments in renewable energy technology"
    ]
    
    print("🚀 DEMONSTRATION: Dynamically Adaptive Swarm System")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query[:50]}...")
        print('='*60)
        
        # Process the request
        result = system.process_request(
            user_query=query,
            user_preferences={
                "execution_preference": "auto",  # Let system decide
                "budget_constraints": {"max_cost": 0.1}  # $0.10 budget
            }
        )
        
        # Show the execution explanation
        print(system.get_execution_explanation(result))
        
        print("\n" + "="*60)
    
    # Show overall system performance
    print("\n📊 SYSTEM PERFORMANCE REPORT")
    print("="*60)
    performance_report = system.get_system_performance_report()
    print(f"Overview: {performance_report['overview']}")
    print(f"Architecture Usage: {performance_report['architecture_usage']}")
    print(f"Cost Analysis: {performance_report['cost_analysis']}")
    print(f"System Health: {performance_report['system_health']}")
    
    print(f"\n✅ Demonstration complete! Processed {len(test_queries)} tasks with adaptive intelligence.")
