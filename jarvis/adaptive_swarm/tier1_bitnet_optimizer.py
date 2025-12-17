# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Tier 1: BitNet 1-Bit Architecture Selector

This module implements the first tier of the adaptive swarm system.
It uses a 1-bit model (when available) to analyze user queries and extract
task characteristics, then selects the optimal architecture using the
agent-scaling-laws scientific framework.

Features:
- 1-bit model inference for lightweight task analysis
- Scientific architecture selection based on scaling laws
- Fallback to regular models when 1-bit isn't available
- Extracts 5 key metrics: parallelizable, dynamic, sequential, tool_intensive, complexity
"""

import json
import logging
import subprocess
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass

from agent_scaling_laws.models import ArchitectureSelector
from agent_scaling_laws.models.architecture_selector import TaskCharacteristics, AgentCapabilities

logger = logging.getLogger(__name__)

ArchitectureType = Literal["single", "independent", "centralized", "decentralized", "hybrid"]


@dataclass
class TaskAnalysis:
    """Result of task analysis with characteristics and recommendations."""
    
    # Task characteristics extracted from prompt
    parallelizable: float
    dynamic: float  
    sequential: float
    tool_intensive: float
    complexity: float
    
    # Architecture recommendation
    selected_architecture: ArchitectureType
    confidence: float
    
    # Scientific explanation
    scores: Dict[ArchitectureType, float]
    reasoning: list[str]
    
    # Processing metadata
    model_used: str
    processing_time: float


class BitNetOptimizer:
    """
    BitNet 1-Bit Architecture Selector.
    
    Uses lightweight 1-bit models to analyze tasks and select optimal
    architectures based on scientific scaling laws. Falls back to regular
    models when 1-bit models aren't available.
    """
    
    def __init__(self):
        """Initialize the BitNet optimizer."""
        self.selector = ArchitectureSelector()
        self.bitnet_available = self._check_bitnet_availability()
        self.model_path = self._locate_1bit_model()
        
        # Model configurations
        self.models = {
            "bitnet": {
                "model": self.model_path,
                "max_tokens": 100,
                "temperature": 0.1,  # Lower temperature for consistent analysis
                "host": "localhost:11434"
            },
            "fallback": {
                "model": "llama3.1:8b", 
                "max_tokens": 200,
                "temperature": 0.3,
                "host": "localhost:11434"
            }
        }
        
        logger.info(f"BitNet Optimizer initialized - BitNet available: {self.bitnet_available}")
    
    def _check_bitnet_availability(self) -> bool:
        """
        Check if 1-bit models are available.
        
        Returns:
            True if BitNet models are available
        """
        try:
            # Check for common BitNet model names
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                models = result.stdout.lower()
                bitnet_indicators = ["bitnet", "b1.58", "1bit", "gguf"]
                return any(indicator in models for indicator in bitnet_indicators)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return False
    
    def _locate_1bit_model(self) -> Optional[str]:
        """
        Locate available 1-bit model.
        
        Returns:
            Model name for 1-bit model or None
        """
        if not self.bitnet_available:
            return None
            
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if any(indicator in line.lower() for indicator in ["bitnet", "b1.58", "1bit"]):
                        # Extract model name from line like "llama3.1:8b-bitnet"
                        parts = line.split()
                        if parts:
                            return parts[0]
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None
    
    def analyze_task_characteristics(self, user_query: str) -> Dict[str, float]:
        """
        Analyze user query to extract task characteristics.
        
        Uses 1-bit model when available, falls back to regular model.
        
        Args:
            user_query: The user's query to analyze
            
        Returns:
            Dictionary with 5 characteristic metrics (0.0 to 1.0)
        """
        import time
        start_time = time.time()
        
        # Use 1-bit model if available, otherwise fallback
        model_config = self.models["bitnet"] if self.bitnet_available else self.models["fallback"]
        
        prompt = self._build_analysis_prompt(user_query)
        
        try:
            # Simulate 1-bit inference call
            # In real implementation, this would call bitnet.cpp or Ollama
            characteristics = self._call_bitnet_model(prompt, model_config)
            
            processing_time = time.time() - start_time
            logger.info(f"Task analysis completed in {processing_time:.2f}s using {model_config['model']}")
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            # Return default characteristics as fallback
            return self._get_default_characteristics()
    
    def _build_analysis_prompt(self, user_query: str) -> str:
        """
        Build prompt for task characteristic analysis.
        
        Args:
            user_query: User query to analyze
            
        Returns:
            Formatted prompt for the model
        """
        return f"""
Analyze this user query and rate these characteristics from 0.0 to 1.0:

**User Query:** "{user_query}"

**Rate these characteristics (0.0 = not at all, 1.0 = extremely):**

1. **Parallelizable**: Can parts of this task run simultaneously?
   - Examples: file analysis, multiple searches, parallel processing

2. **Dynamic**: Does the task require adaptation or real-time changes?
   - Examples: conversational tasks, iterative refinement, flexible workflows

3. **Sequential**: Must step A complete before step B can start?
   - Examples: step-by-step instructions, logical dependencies

4. **ToolIntensive**: Does the task require external tools (search, calculation, APIs)?
   - Examples: web research, data analysis, complex computations

5. **Complexity**: How difficult is this task overall?
   - Examples: simple questions vs. complex analysis

**Respond with JSON only:**
{{
  "parallelizable": 0.0-1.0,
  "dynamic": 0.0-1.0, 
  "sequential": 0.0-1.0,
  "tool_intensive": 0.0-1.0,
  "complexity": 0.0-1.0
}}
"""
    
    def _call_bitnet_model(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, float]:
        """
        Call 1-bit model for task analysis.
        
        Args:
            prompt: Analysis prompt
            model_config: Model configuration
            
        Returns:
            Task characteristics dictionary
        """
        # This is a placeholder implementation
        # In reality, this would call Ollama API or bitnet.cpp
        
        # Simulate different responses based on query content
        if "analyze" in prompt.lower() and "file" in prompt.lower():
            # File analysis = high parallelizable, moderate complexity
            return {
                "parallelizable": 0.8,
                "dynamic": 0.3,
                "sequential": 0.2,
                "tool_intensive": 0.6,
                "complexity": 0.5
            }
        elif "write" in prompt.lower() or "create" in prompt.lower():
            # Writing tasks = low parallelizable, moderate complexity
            return {
                "parallelizable": 0.2,
                "dynamic": 0.4,
                "sequential": 0.8,
                "tool_intensive": 0.3,
                "complexity": 0.6
            }
        elif "research" in prompt.lower():
            # Research tasks = high parallelizable, high tool intensity
            return {
                "parallelizable": 0.7,
                "dynamic": 0.5,
                "sequential": 0.3,
                "tool_intensive": 0.8,
                "complexity": 0.7
            }
        else:
            # Default balanced characteristics
            return {
                "parallelizable": 0.5,
                "dynamic": 0.5,
                "sequential": 0.5,
                "tool_intensive": 0.5,
                "complexity": 0.5
            }
    
    def _get_default_characteristics(self) -> Dict[str, float]:
        """
        Return default task characteristics as fallback.
        
        Returns:
            Default characteristic values
        """
        return {
            "parallelizable": 0.5,
            "dynamic": 0.5,
            "sequential": 0.5,
            "tool_intensive": 0.5,
            "complexity": 0.5
        }
    
    def select_optimal_architecture(
        self, 
        user_query: str,
        agent_capabilities: Optional[AgentCapabilities] = None
    ) -> TaskAnalysis:
        """
        Complete architecture selection pipeline.
        
        Args:
            user_query: User query to analyze
            agent_capabilities: Agent capabilities (uses defaults if None)
            
        Returns:
            Complete task analysis with architecture recommendation
        """
        import time
        start_time = time.time()
        
        # Use default capabilities if not provided
        if agent_capabilities is None:
            agent_capabilities = AgentCapabilities(
                baseline_accuracy=0.6,
                token_budget=100000,
                model_capability=0.6
            )
        
        # Extract task characteristics
        characteristics = self.analyze_task_characteristics(user_query)
        
        # Create TaskCharacteristics object
        task = TaskCharacteristics(**characteristics)
        
        # Use scientific architecture selector
        selection_result = self.selector.explain_selection(task, agent_capabilities)
        
        processing_time = time.time() - start_time
        
        # Create comprehensive analysis result
        return TaskAnalysis(
            parallelizable=characteristics["parallelizable"],
            dynamic=characteristics["dynamic"],
            sequential=characteristics["sequential"],
            tool_intensive=characteristics["tool_intensive"],
            complexity=characteristics["complexity"],
            selected_architecture=selection_result["selected_architecture"],
            confidence=max(selection_result["scores"].values()) if selection_result["scores"] else 0.0,
            scores=selection_result["scores"],
            reasoning=selection_result["reasoning"],
            model_used=self.models["bitnet"]["model"] if self.bitnet_available else self.models["fallback"]["model"],
            processing_time=processing_time
        )
    
    def get_optimization_explanation(self, analysis: TaskAnalysis) -> str:
        """
        Generate human-readable explanation of the optimization.
        
        Args:
            analysis: Task analysis result
            
        Returns:
            Human-readable explanation
        """
        explanation = f"""
🧠 **Architecture Optimization Analysis**

**Query Analysis:**
- Model Used: {analysis.model_used}
- Processing Time: {analysis.processing_time:.2f}s
- Confidence: {analysis.confidence:.3f}

**Task Characteristics:**
- Parallelizable: {analysis.parallelizable:.1f} (can run simultaneously)
- Dynamic: {analysis.dynamic:.1f} (needs adaptation)  
- Sequential: {analysis.sequential:.1f} (step-by-step dependency)
- Tool Intensive: {analysis.tool_intensive:.1f} (requires external tools)
- Complexity: {analysis.complexity:.1f} (difficulty level)

**Recommended Architecture:** {analysis.selected_architecture.upper()}

**Why This Choice:**
"""
        
        for reason in analysis.reasoning:
            explanation += f"- {reason}\n"
        
        explanation += f"""
**Performance Predictions:**
- Single Agent: {analysis.scores.get('single', 0):.3f}
- Independent: {analysis.scores.get('independent', 0):.3f}  
- Centralized: {analysis.scores.get('centralized', 0):.3f}
- Decentralized: {analysis.scores.get('decentralized', 0):.3f}
- Hybrid: {analysis.scores.get('hybrid', 0):.3f}
"""
        
        return explanation


# Example usage
if __name__ == "__main__":
    optimizer = BitNetOptimizer()
    
    # Test with different query types
    test_queries = [
        "Analyze these 5 python files and find bugs",
        "Write a comprehensive report about AI trends", 
        "Research quantum computing developments"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        analysis = optimizer.select_optimal_architecture(query)
        print(optimizer.get_optimization_explanation(analysis))
