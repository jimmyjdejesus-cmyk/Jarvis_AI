"""
Model Router for intelligent request routing
"""
import re
import logging
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class ModelRouter:
    """Intelligent routing of requests to best models"""
    
    def __init__(self, mcp_client):
        """
        Initialize model router
        
        Args:
            mcp_client: MCP client instance for communication
        """
        self.mcp_client = mcp_client
        
        # Model capabilities mapping
        self.model_capabilities = {
            "code_review": {
                "models": ["claude-3.5-sonnet", "gpt-4", "llama3.2"],
                "priority": ["claude-3.5-sonnet", "gpt-4", "llama3.2"],
                "fallback": "llama3.2"
            },
            "code_generation": {
                "models": ["gpt-4", "claude-3.5-sonnet", "llama3.2"],
                "priority": ["gpt-4", "claude-3.5-sonnet", "llama3.2"],
                "fallback": "llama3.2"
            },
            "quick_question": {
                "models": ["llama3.2", "gpt-3.5-turbo"],
                "priority": ["llama3.2", "gpt-3.5-turbo"],
                "fallback": "llama3.2"
            },
            "research": {
                "models": ["gemini-pro", "gpt-4", "claude-3.5-sonnet"],
                "priority": ["gpt-4", "claude-3.5-sonnet", "gemini-pro"],
                "fallback": "llama3.2"
            },
            "analysis": {
                "models": ["claude-3.5-sonnet", "gpt-4"],
                "priority": ["claude-3.5-sonnet", "gpt-4"],
                "fallback": "llama3.2"
            },
            "general": {
                "models": ["llama3.2", "gpt-3.5-turbo"],
                "priority": ["llama3.2"],
                "fallback": "llama3.2"
            }
        }
        
        # Classification patterns
        self.classification_patterns = {
            "code_review": [
                r"review.*code", r"check.*code", r"analyze.*code",
                r"code.*review", r"look.*code", r"improve.*code"
            ],
            "code_generation": [
                r"generate.*code", r"create.*function", r"write.*code",
                r"build.*application", r"implement.*feature", r"develop.*system"
            ],
            "quick_question": [
                r"^what\s", r"^how\s", r"^why\s", r"^when\s", r"^where\s",
                r"^is\s", r"^can\s", r"^do\s", r"^does\s"
            ],
            "research": [
                r"research", r"investigate", r"find.*information",
                r"tell.*about", r"explain.*detail", r"comprehensive"
            ],
            "analysis": [
                r"analyze", r"examine", r"evaluate", r"assess",
                r"compare", r"study", r"breakdown"
            ]
        }
    
    async def classify_request(self, message: str) -> Dict[str, Any]:
        """
        Classify request type and complexity
        
        Args:
            message: User message to classify
            
        Returns:
            Classification result with type, complexity, and confidence
        """
        message_lower = message.lower().strip()
        
        # Initialize scores
        scores = {category: 0 for category in self.classification_patterns}
        
        # Pattern matching
        for category, patterns in self.classification_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    scores[category] += 1
        
        # Additional heuristics
        if len(message.split()) > 50:
            scores["research"] += 1
            scores["analysis"] += 1
        
        if any(word in message_lower for word in ["bug", "error", "issue", "problem"]):
            scores["code_review"] += 2
        
        if any(word in message_lower for word in ["secure", "security", "auth", "permission"]):
            scores["analysis"] += 1
        
        # Determine best category
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # If no clear winner, default to general
        if max_score == 0:
            best_category = "general"
        
        # Determine complexity
        complexity = self._assess_complexity(message_lower)
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = max_score / max(total_score, 1) if total_score > 0 else 0.5
        
        return {
            "type": best_category,
            "complexity": complexity,
            "confidence": confidence,
            "scores": scores,
            "message_length": len(message),
            "word_count": len(message.split())
        }
    
    def _assess_complexity(self, message: str) -> str:
        """Assess the complexity of a message"""
        word_count = len(message.split())
        
        # Complexity indicators
        complex_words = [
            "architecture", "infrastructure", "enterprise", "scalable",
            "distributed", "microservices", "kubernetes", "docker",
            "production", "deployment", "ci/cd", "devops"
        ]
        
        complexity_score = 0
        
        # Word count factor
        if word_count > 100:
            complexity_score += 2
        elif word_count > 50:
            complexity_score += 1
        
        # Complex terminology
        for word in complex_words:
            if word in message:
                complexity_score += 1
        
        # Multiple questions/requests
        if message.count("?") > 2:
            complexity_score += 1
        
        # Classify complexity
        if complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    async def route_to_best_model(self, message: str, force_local: bool = False) -> str:
        """
        Route message to best available model
        
        Args:
            message: User message
            force_local: Force use of local models only
            
        Returns:
            Generated response
        """
        # Classify the request
        classification = await self.classify_request(message)
        request_type = classification["type"]
        
        logger.info(f"Classified request as: {request_type} (confidence: {classification['confidence']:.2f})")
        
        # Get suitable models for this task type
        capability_config = self.model_capabilities.get(request_type, self.model_capabilities["general"])
        suitable_models = capability_config["priority"]
        fallback_model = capability_config["fallback"]
        
        # If forcing local, filter to local models only
        if force_local:
            local_models = ["llama3.2"]  # Add other local models as available
            suitable_models = [m for m in suitable_models if m in local_models]
            if not suitable_models:
                suitable_models = [fallback_model]
        
        # Try models in preference order
        last_error = None
        for model in suitable_models:
            try:
                logger.info(f"Trying model: {model}")
                
                # Determine which server has this model
                server = self._get_server_for_model(model)
                
                if server:
                    response = await self.mcp_client.generate_response(
                        server=server,
                        model=model,
                        prompt=message
                    )
                    
                    logger.info(f"Successfully generated response using {model}")
                    return response
                else:
                    logger.warning(f"No server available for model: {model}")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to use model {model}: {e}")
                continue
        
        # If all models failed, try fallback
        try:
            logger.info(f"Falling back to: {fallback_model}")
            server = self._get_server_for_model(fallback_model)
            
            if server:
                response = await self.mcp_client.generate_response(
                    server=server,
                    model=fallback_model,
                    prompt=message
                )
                return response
        except Exception as e:
            last_error = e
        
        # If everything failed
        error_msg = f"All models failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _get_server_for_model(self, model: str) -> Optional[str]:
        """
        Determine which server hosts a given model
        
        Args:
            model: Model name
            
        Returns:
            Server name or None if not found
        """
        # Model to server mapping
        model_servers = {
            "llama3.2": "ollama",
            "llama3.1": "ollama", 
            "llama3": "ollama",
            "gpt-4": "openai",
            "gpt-3.5-turbo": "openai",
            "claude-3.5-sonnet": "anthropic",
            "claude-3": "anthropic",
            "gemini-pro": "google"
        }
        
        return model_servers.get(model, "ollama")  # Default to ollama
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models by category"""
        return {
            category: config["models"] 
            for category, config in self.model_capabilities.items()
        }
    
    def add_model_capability(self, category: str, models: List[str], priority: List[str] = None):
        """
        Add or update model capability configuration
        
        Args:
            category: Task category
            models: Available models for this category
            priority: Priority order (defaults to same as models)
        """
        self.model_capabilities[category] = {
            "models": models,
            "priority": priority or models,
            "fallback": models[0] if models else "llama3.2"
        }
