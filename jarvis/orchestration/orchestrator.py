"""
Multi-Agent Orchestrator
Coordinates multiple specialist agents for complex tasks with an optional
red-team critic that verifies each specialist's output for logical errors
and conflicting assumptions.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
import yaml

from ..agents.specialists import (
    CodeReviewAgent,
    SecurityAgent,
    ArchitectureAgent,
    TestingAgent,
    DevOpsAgent
)
from ..agents.critics import RedTeamCritic

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """Coordinates multiple specialist agents and optional red-team critique."""
    
    def __init__(self, mcp_client):
        """
        Initialize multi-agent orchestrator

        Args:
            mcp_client: MCP client for agent communication
        """
        self.mcp_client = mcp_client

        # Initialize specialist agents
        self.specialists = {
            "code_review": CodeReviewAgent(mcp_client),
            "security": SecurityAgent(mcp_client),
            "architecture": ArchitectureAgent(mcp_client),
            "testing": TestingAgent(mcp_client),
            "devops": DevOpsAgent(mcp_client)
        }

        # Optional red team critic
        self.critic = None
        config_path = Path(__file__).resolve().parents[2] / "config" / "default.yaml"
        enable_red_team = False
        if config_path.exists():
            try:
                config_data = yaml.safe_load(config_path.read_text()) or {}
                enable_red_team = bool(config_data.get("ENABLE_RED_TEAM", False))
            except Exception as e:
                logger.warning(f"Failed to load red team config: {e}")
        if os.getenv("ENABLE_RED_TEAM") is not None:
            env_val = os.getenv("ENABLE_RED_TEAM", "false").lower()
            enable_red_team = env_val in ("1", "true", "yes", "on")
        if enable_red_team:
            self.critic = RedTeamCritic(mcp_client)

        self.task_history = []
        self.active_collaborations = {}
        
        # Agent collaboration rules
        self.collaboration_patterns = {
            "code_review": {
                "always_collaborate": ["security"],
                "often_collaborate": ["testing"],
                "sometimes_collaborate": ["architecture", "devops"]
            },
            "security": {
                "always_collaborate": ["code_review"],
                "often_collaborate": ["architecture"],
                "sometimes_collaborate": ["testing", "devops"]
            },
            "architecture": {
                "always_collaborate": ["security"],
                "often_collaborate": ["devops"],
                "sometimes_collaborate": ["code_review", "testing"]
            },
            "testing": {
                "often_collaborate": ["code_review"],
                "sometimes_collaborate": ["security", "architecture", "devops"]
            },
            "devops": {
                "often_collaborate": ["architecture", "security"],
                "sometimes_collaborate": ["code_review", "testing"]
            }
        }
    
    async def analyze_request_complexity(self, request: str, code: str = None) -> Dict[str, Any]:
        """
        Analyze request to determine complexity and required specialists
        
        Args:
            request: User request description
            code: Optional code to analyze
            
        Returns:
            Analysis of complexity and required specialists
        """
        request_lower = request.lower()
        
        # Complexity indicators
        complexity_indicators = {
            "high": [
                "architecture", "design", "system", "migrate", "refactor", 
                "enterprise", "scale", "production", "deploy", "infrastructure",
                "security audit", "comprehensive", "full review"
            ],
            "medium": [
                "review", "improve", "optimize", "analyze", "test", "security",
                "performance", "best practices", "refactor", "debug"
            ],
            "low": [
                "fix", "simple", "quick", "basic", "help", "explain", "what is"
            ]
        }
        
        # Determine complexity
        complexity = "low"
        for level, indicators in complexity_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                complexity = level
                break
        
        # Identify needed specialists
        specialist_triggers = {
            "code_review": [
                "review", "code", "check", "improve", "quality", "best practices",
                "bugs", "optimize", "refactor", "clean"
            ],
            "security": [
                "security", "secure", "vulnerability", "auth", "permission",
                "encrypt", "protect", "compliance", "audit", "threat"
            ],
            "architecture": [
                "architecture", "design", "system", "pattern", "structure",
                "scalable", "microservices", "api", "database", "integration"
            ],
            "testing": [
                "test", "testing", "coverage", "quality", "qa", "validation",
                "unit test", "integration", "e2e", "automated"
            ],
            "devops": [
                "deploy", "deployment", "ci/cd", "pipeline", "infrastructure",
                "docker", "kubernetes", "cloud", "monitoring", "automation"
            ]
        }
        
        needed_specialists = []
        specialist_scores = {}
        
        for specialist, triggers in specialist_triggers.items():
            score = sum(1 for trigger in triggers if trigger in request_lower)
            specialist_scores[specialist] = score
            
            if score > 0:
                needed_specialists.append(specialist)
        
        # Always include code_review if code is provided
        if code and "code_review" not in needed_specialists:
            needed_specialists.append("code_review")
            specialist_scores["code_review"] = 1
        
        # Sort specialists by relevance score
        needed_specialists.sort(key=lambda x: specialist_scores.get(x, 0), reverse=True)
        
        # Determine coordination strategy
        coordination_type = self._determine_coordination_type(needed_specialists, complexity)
        
        return {
            "complexity": complexity,
            "specialists_needed": needed_specialists,
            "specialist_scores": specialist_scores,
            "estimated_time": self._estimate_processing_time(complexity, len(needed_specialists)),
            "coordination_type": coordination_type,
            "collaboration_depth": self._determine_collaboration_depth(needed_specialists)
        }
    
    def _determine_coordination_type(self, specialists: List[str], complexity: str) -> str:
        """Determine how specialists should be coordinated"""
        if len(specialists) <= 1:
            return "single"
        elif len(specialists) == 2 and complexity in ["low", "medium"]:
            return "parallel"
        elif complexity == "high" or len(specialists) > 3:
            return "sequential"
        else:
            return "parallel"
    
    def _determine_collaboration_depth(self, specialists: List[str]) -> str:
        """Determine depth of collaboration between specialists"""
        if len(specialists) <= 1:
            return "none"
        elif len(specialists) == 2:
            return "basic"
        elif len(specialists) <= 3:
            return "moderate"
        else:
            return "deep"
    
    async def coordinate_specialists(self, request: str, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """
        Coordinate multiple specialists to handle complex request
        
        Args:
            request: User request
            code: Optional code to analyze
            user_context: Additional user context
            
        Returns:
            Coordinated analysis results
        """
        # Analyze request complexity
        analysis = await self.analyze_request_complexity(request, code)
        
        if not analysis["specialists_needed"]:
            return self._create_simple_response(request)
        
        logger.info(f"Coordinating {len(analysis['specialists_needed'])} specialists for {analysis['complexity']} complexity task")
        
        # Execute coordination strategy
        if analysis["coordination_type"] == "single":
            return await self._single_specialist_analysis(request, analysis, code, user_context)
        elif analysis["coordination_type"] == "parallel":
            return await self._parallel_specialist_analysis(request, analysis, code, user_context)
        else:  # sequential
            return await self._sequential_specialist_analysis(request, analysis, code, user_context)
    
    async def _single_specialist_analysis(self, request: str, analysis: Dict, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with single specialist"""
        specialist_type = analysis["specialists_needed"][0]
        specialist = self.specialists[specialist_type]
        
        # Create task with full context
        task = self._create_specialist_task(request, code, user_context)
        try:
            result = await specialist.process_task(task, context=None, user_context=user_context)
            if self.critic:
                critique = await self.critic.review(specialist_type, result.get("response", ""))
                result["critic"] = critique

            return {
                "type": "single_specialist",
                "complexity": analysis["complexity"],
                "specialists_used": [specialist_type],
                "results": {specialist_type: result},
                "synthesized_response": result["response"],
                "confidence": result["confidence"],
                "coordination_summary": f"Analysis completed by {specialist_type} specialist",
            }
            
        except Exception as e:
            logger.error(f"Single specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    async def _parallel_specialist_analysis(self, request: str, analysis: Dict, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with parallel specialist coordination"""
        specialists_needed = analysis["specialists_needed"]
        
        # Create tasks for all specialists
        task = self._create_specialist_task(request, code, user_context)
        
        # Run specialists in parallel
        tasks = []
        for specialist_type in specialists_needed:
            specialist = self.specialists[specialist_type]
            tasks.append(specialist.process_task(task, context=None, user_context=user_context))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            specialist_results = {}
            successful_results = []
            
            for i, result in enumerate(results):
                specialist_type = specialists_needed[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Specialist {specialist_type} failed: {result}")
                    specialist_results[specialist_type] = self._create_specialist_error(specialist_type, str(result))
                else:
                    specialist_results[specialist_type] = result
                    successful_results.append(result)
                    if self.critic:
                        critique = await self.critic.review(specialist_type, result.get("response", ""))
                        result["critic"] = critique
            
            # Synthesize results
            synthesized_response = await self._synthesize_parallel_results(request, successful_results)
            overall_confidence = self._calculate_overall_confidence(successful_results)
            
            return {
                "type": "parallel_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": overall_confidence,
                "coordination_summary": f"Parallel analysis by {len(successful_results)} specialists"
            }
            
        except Exception as e:
            logger.error(f"Parallel specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    async def _sequential_specialist_analysis(self, request: str, analysis: Dict, code: str = None, user_context: str = None) -> Dict[str, Any]:
        """Handle analysis with sequential specialist coordination"""
        specialists_needed = analysis["specialists_needed"]
        
        # Build context progressively
        shared_context = []
        specialist_results = {}
        
        task = self._create_specialist_task(request, code, user_context)
        
        try:
            for specialist_type in specialists_needed:
                specialist = self.specialists[specialist_type]
                
                # Process with accumulated context
                result = await specialist.process_task(task, context=shared_context, user_context=user_context)
                if self.critic:
                    critique = await self.critic.review(specialist_type, result.get("response", ""))
                    result["critic"] = critique
                specialist_results[specialist_type] = result
                
                # Add result to shared context for next specialists
                shared_context.append({
                    "specialist": specialist_type,
                    "key_points": result.get("suggestions", [])[:3],  # Top 3 suggestions
                    "confidence": result.get("confidence", 0.7),
                    "priority_issues": result.get("priority_issues", [])[:2]  # Top 2 issues
                })
                
                logger.info(f"Completed {specialist_type} analysis, passing context to next specialist")
            
            # Final synthesis with all results
            synthesized_response = await self._synthesize_sequential_results(request, specialist_results)
            overall_confidence = self._calculate_overall_confidence(list(specialist_results.values()))
            
            return {
                "type": "sequential_specialists",
                "complexity": analysis["complexity"],
                "specialists_used": specialists_needed,
                "results": specialist_results,
                "synthesized_response": synthesized_response,
                "confidence": overall_confidence,
                "coordination_summary": f"Sequential analysis with {len(specialists_needed)} specialists building on each other's insights"
            }
            
        except Exception as e:
            logger.error(f"Sequential specialist analysis failed: {e}")
            return self._create_error_response(str(e), request)
    
    def _create_specialist_task(self, request: str, code: str = None, user_context: str = None) -> str:
        """Create comprehensive task description for specialists"""
        task_parts = [request]
        
        if code:
            task_parts.append(f"\n**Code to Analyze:**\n```\n{code}\n```")
        
        if user_context:
            task_parts.append(f"\n**Additional Context:**\n{user_context}")
        
        return "\n".join(task_parts)
    
    async def _synthesize_parallel_results(self, original_request: str, results: List[Dict]) -> str:
        """Synthesize results from parallel specialist analysis"""
        if not results:
            return "No successful analysis results to synthesize."
        
        synthesis_prompt = f"""
        **MULTI-SPECIALIST ANALYSIS SYNTHESIS**
        
        Original Request: {original_request}
        
        **Specialist Insights:**
        """
        
        for result in results:
            specialist = result.get("specialist", "unknown")
            confidence = result.get("confidence", 0.0)
            response = result.get("response", "No response")[:300]  # Limit length
            
            synthesis_prompt += f"\n**{specialist.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        synthesis_prompt += """
        
        **Your Task:**
        Synthesize these expert opinions into a comprehensive, actionable response.
        - Highlight areas of agreement and any conflicts
        - Prioritize recommendations by importance and feasibility
        - Provide a clear action plan
        - Maintain the technical accuracy of each specialist's input
        """
        
        try:
            # Use the best available model for synthesis
            synthesis_response = await self.mcp_client.generate_response(
                server="ollama",
                model="llama3.2",
                prompt=synthesis_prompt
            )
            
            return synthesis_response
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._create_fallback_synthesis(results)
    
    async def _synthesize_sequential_results(self, original_request: str, results: Dict[str, Dict]) -> str:
        """Synthesize results from sequential specialist analysis"""
        synthesis_prompt = f"""
        **SEQUENTIAL MULTI-SPECIALIST ANALYSIS SYNTHESIS**
        
        Original Request: {original_request}
        
        **Sequential Expert Analysis:**
        """
        
        for specialist_type, result in results.items():
            confidence = result.get("confidence", 0.0)
            response = result.get("response", "No response")[:300]
            
            synthesis_prompt += f"\n**{specialist_type.title()} Expert** (confidence: {confidence:.2f}):\n{response}...\n"
        
        synthesis_prompt += """
        
        **Your Task:**
        Synthesize this sequential analysis into a comprehensive response.
        - Each specialist built upon previous insights
        - Integrate the progressive understanding developed
        - Provide unified recommendations that consider all perspectives
        - Create a coherent action plan
        """
        
        try:
            synthesis_response = await self.mcp_client.generate_response(
                server="ollama",
                model="llama3.2",
                prompt=synthesis_prompt
            )
            
            return synthesis_response
            
        except Exception as e:
            logger.error(f"Sequential synthesis failed: {e}")
            return self._create_fallback_synthesis(list(results.values()))
    
    def _create_fallback_synthesis(self, results: List[Dict]) -> str:
        """Create fallback synthesis when AI synthesis fails"""
        synthesis = "## Multi-Specialist Analysis Summary\n\n"
        
        for result in results:
            specialist = result.get("specialist", "unknown")
            suggestions = result.get("suggestions", [])
            priority_issues = result.get("priority_issues", [])
            
            synthesis += f"### {specialist.title()} Expert Insights:\n"
            
            if suggestions:
                synthesis += "**Key Recommendations:**\n"
                for suggestion in suggestions[:3]:
                    synthesis += f"- {suggestion}\n"
            
            if priority_issues:
                synthesis += "**Priority Issues:**\n"
                for issue in priority_issues[:2]:
                    synthesis += f"- {issue.get('description', 'Unknown issue')}\n"
            
            synthesis += "\n"
        
        synthesis += "**Next Steps:** Review each specialist's recommendations and prioritize based on your specific needs and constraints."
        
        return synthesis
    
    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        """Calculate overall confidence from multiple specialist results"""
        if not results:
            return 0.0
        
        confidences = [r.get("confidence", 0.5) for r in results]
        base_confidence = sum(confidences) / len(confidences)
        
        # Boost confidence when multiple specialists agree
        if len(results) > 1:
            base_confidence += min(0.1 * (len(results) - 1), 0.3)
        
        return min(base_confidence, 1.0)
    
    def _estimate_processing_time(self, complexity: str, num_specialists: int) -> str:
        """Estimate processing time for analysis"""
        base_times = {"low": 10, "medium": 20, "high": 40}
        estimated_seconds = base_times[complexity] * num_specialists
        
        if estimated_seconds < 60:
            return f"{estimated_seconds} seconds"
        else:
            return f"{estimated_seconds // 60} minutes"
    
    def _create_simple_response(self, request: str) -> Dict[str, Any]:
        """Create response for simple requests that don't need specialists"""
        return {
            "type": "simple",
            "complexity": "low",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"This appears to be a simple request that doesn't require specialist analysis: {request}",
            "confidence": 0.6,
            "coordination_summary": "No specialist coordination needed"
        }
    
    def _create_error_response(self, error_msg: str, request: str) -> Dict[str, Any]:
        """Create error response when coordination fails"""
        return {
            "type": "error",
            "complexity": "unknown",
            "specialists_used": [],
            "results": {},
            "synthesized_response": f"I apologize, but I encountered an error while coordinating specialist analysis for your request: {error_msg}",
            "confidence": 0.0,
            "error": True,
            "coordination_summary": f"Coordination failed: {error_msg}"
        }
    
    def _create_specialist_error(self, specialist_type: str, error_msg: str) -> Dict[str, Any]:
        """Create error result for failed specialist"""
        return {
            "specialist": specialist_type,
            "response": f"Analysis failed: {error_msg}",
            "confidence": 0.0,
            "suggestions": [],
            "priority_issues": [],
            "error": True
        }
    
    def get_specialist_status(self) -> Dict[str, Any]:
        """Get status of all specialists"""
        status = {}
        
        for name, specialist in self.specialists.items():
            status[name] = specialist.get_specialization_info()
        
        return {
            "available_specialists": list(self.specialists.keys()),
            "specialist_details": status,
            "total_tasks_completed": sum(len(s.task_history) for s in self.specialists.values()),
            "collaboration_patterns": self.collaboration_patterns
        }
    
    async def health_check_specialists(self) -> Dict[str, Any]:
        """Perform health check on all specialists"""
        health_results = {}
        
        test_task = "Health check test"
        
        for name, specialist in self.specialists.items():
            try:
                # Simple test to verify specialist is working
                result = await specialist.process_task(test_task)
                health_results[name] = {
                    "status": "healthy",
                    "confidence": result.get("confidence", 0.0),
                    "model_used": result.get("model_used", "unknown")
                }
            except Exception as e:
                health_results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        overall_health = "healthy" if all(
            h.get("status") == "healthy" for h in health_results.values()
        ) else "degraded"
        
        return {
            "overall_status": overall_health,
            "specialists": health_results,
            "timestamp": datetime.now().isoformat()
        }
