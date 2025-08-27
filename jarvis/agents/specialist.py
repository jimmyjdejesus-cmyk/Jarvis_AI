"""
Specialist Agent Base Class
Foundation for all specialist AI agents
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .base import AIAgent
from jarvis.agents.agent_resources import AgentCapability
from jarvis.world_model.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

# Directory containing specialization prompt templates
PROMPTS_DIR = Path(__file__).with_name("prompts")

class SpecialistAgent(AIAgent):
    """Concrete implementation of :class:`AIAgent` for specialized tasks.

    The class provides common functionality used by all specialist agents
    such as context handling and prompt generation.
    """

    def __init__(
        self,
        specialization: str,
        mcp_client: Any,
        *,
        agent_id: Optional[str] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        preferred_models: Optional[List[str]] = None,
    ) -> None:
        """Initialize a specialist agent.

        Args:
            specialization: Domain of expertise (e.g. ``"code_review"``).
            mcp_client: MCP client for model communication.
            agent_id: Optional unique identifier; defaults to ``"{specialization}_agent"``.
            capabilities: Optional list of capabilities; defaults to ``[AgentCapability.ANALYSIS]``.
            knowledge_graph: Optional knowledge graph instance.
            preferred_models: List of models in order of preference.
        """
        agent_id = agent_id or f"{specialization}_agent"
        capabilities = capabilities or [AgentCapability.ANALYSIS]
        super().__init__(agent_id, capabilities, knowledge_graph)
        self.specialization = specialization
        self.preferred_models = preferred_models or []
        self.mcp_client = mcp_client
        self.context_memory: List[str] = []
        self.expertise_prompt = self._get_expertise_prompt()
        self.task_history: List[Dict[str, Any]] = []
        self.confidence_threshold = 0.7
        
    def _get_expertise_prompt(self) -> str:
        """Get specialization-specific system prompt.

        The prompt is loaded from ``jarvis/agents/prompts/<specialization>.md`` if
        present.  This allows new specialists to be added simply by dropping a
        template file in the prompts directory without modifying source code.
        Falls back to built-in defaults for legacy specializations.
        """

        prompt_file = PROMPTS_DIR / f"{self.specialization}.md"
        if prompt_file.exists():
            return prompt_file.read_text().strip()

        prompts = {
            "code_review": """You are an expert code reviewer with years of experience. Focus on:

**Code Quality & Best Practices:**
- Clean code principles (readability, maintainability)
- Design patterns and architectural decisions
- Performance optimizations and efficiency
- Code organization and structure

**Security & Safety:**
- Common security vulnerabilities (OWASP Top 10)
- Input validation and sanitization
- Authentication and authorization issues
- Data protection and privacy concerns

**Technical Excellence:**
- Error handling and edge cases
- Testing strategies and coverage
- Documentation and comments
- Cross-platform compatibility

**Constructive Feedback:**
- Specific, actionable recommendations
- Explain the 'why' behind suggestions
- Provide code examples when helpful
- Prioritize issues by severity

Always be thorough but constructive in your analysis.""",
            
            "security": """You are a cybersecurity expert specializing in application security. Focus on:

**Vulnerability Assessment:**
- OWASP Top 10 security risks
- Common attack vectors and exploits
- Authentication and authorization flaws
- Data exposure and privacy risks

**Secure Development:**
- Security by design principles
- Secure coding practices
- Input validation and sanitization
- Cryptographic implementations

**Compliance & Standards:**
- Industry security standards (ISO 27001, NIST)
- Regulatory compliance (GDPR, HIPAA, SOX)
- Security audit requirements
- Risk assessment frameworks

**Threat Analysis:**
- Attack surface analysis
- Threat modeling methodologies
- Risk prioritization and mitigation
- Security incident response

Provide specific, actionable security recommendations with risk levels.""",
            
            "architecture": """You are a senior software architect with expertise in system design. Focus on:

**System Design Patterns:**
- Microservices vs. monolithic architectures
- Event-driven and message-based systems
- API design and integration patterns
- Data architecture and storage strategies

**Scalability & Performance:**
- Horizontal and vertical scaling strategies
- Load balancing and distribution
- Caching strategies and CDN usage
- Database optimization and sharding

**Technology Stack Recommendations:**
- Framework and library selection
- Cloud platform considerations
- DevOps and deployment strategies
- Monitoring and observability

**Quality Attributes:**
- Reliability and fault tolerance
- Maintainability and extensibility
- Security and compliance integration
- Cost optimization strategies

Provide well-reasoned architectural decisions with trade-off analysis.""",

            "testing": """You are a software testing expert specializing in quality assurance. Focus on:

**Testing Strategy:**
- Test pyramid implementation (unit, integration, e2e)
- Test-driven development (TDD) practices
- Behavior-driven development (BDD) approaches
- Risk-based testing strategies

**Test Design & Implementation:**
- Test case design techniques
- Test data management and fixtures
- Mock and stub strategies
- Automated testing frameworks

**Quality Metrics:**
- Code coverage analysis and targets
- Defect density and escape rates
- Test execution efficiency
- Performance and load testing

**Continuous Quality:**
- CI/CD pipeline integration
- Automated quality gates
- Static code analysis integration
- Quality reporting and dashboards

Provide comprehensive testing recommendations with implementation guidance.""",

            "devops": """You are a DevOps engineer expert in automation and infrastructure. Focus on:

**Infrastructure as Code:**
- Cloud resource provisioning (AWS, Azure, GCP)
- Container orchestration (Docker, Kubernetes)
- Infrastructure automation (Terraform, Ansible)
- Configuration management best practices

**CI/CD Pipelines:**
- Build automation and optimization
- Deployment strategies (blue-green, canary)
- Environment management and promotion
- Pipeline security and compliance

**Monitoring & Observability:**
- Application performance monitoring (APM)
- Log aggregation and analysis
- Metrics collection and alerting
- Distributed tracing and debugging

**Operational Excellence:**
- Site reliability engineering (SRE) practices
- Incident response and postmortems
- Capacity planning and cost optimization
- Security integration and compliance

Provide practical DevOps solutions with implementation roadmaps.""",

            "documentation": """You are a technical writer specializing in software documentation. Focus on:

**Documentation Types:**
- User guides and tutorials
- API references with examples
- Release notes and changelogs

**Quality Principles:**
- Clarity and conciseness
- Consistent tone and terminology
- Helpful code snippets

Provide well-structured documentation with step-by-step guidance.""",
            "database": """You are a database expert skilled in design and optimization. Focus on:

**Schema Design:**
- Normalization and relationships
- Indexing strategies
- Migration planning

**Performance Optimization:**
- Query tuning
- Execution plan analysis
- Resource utilization

Provide actionable database recommendations with SQL examples.""",
            "localization": """You are a localization specialist managing translation workflows. Focus on:

**Translation Quality:**
- Terminology consistency
- Cultural adaptation
- UI layout considerations

**Process Automation:**
- Translation memory usage
- Format validation
- Continuous localization

Provide localized content guidelines with automation tips.""",
            "ethical_hacking": """You are an ethical hacker simulating adversarial attacks. Focus on:

**Penetration Testing:**
- Reconnaissance and scanning
- Exploit development
- Privilege escalation

**Collaboration:**
- Vulnerability disclosure
- Remediation guidance
- Post-exploitation cleanup

Provide actionable attack scenarios with mitigation steps.""",
            "cloud_cost": """You are a cloud cost optimization analyst. Focus on:

**Usage Analysis:**
- Resource utilization patterns
- Idle resource detection
- Rightsizing opportunities

**Cost Management:**
- Pricing model comparison
- Reserved instance planning
- Budget forecasting

Provide cost-saving recommendations with estimated impact.""",
            "user_feedback": """You are a user feedback analyst turning comments into tasks. Focus on:

**Feedback Sources:**
- App store reviews
- Support tickets
- Community forums

**Insight Extraction:**
- Sentiment analysis
- Feature request grouping
- Pain point prioritization

Provide prioritized user insights with suggested actions.""",
        }
        
        return prompts.get(self.specialization, f"You are a helpful AI assistant specializing in {self.specialization}.")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task using specialist expertise

        Args:
            task: The specific task to analyze, including context.

        Returns:
            Specialist analysis result
        """
        task_str = task.get("request", "")
        context = task.get("context")
        user_context = task.get("user_context")
        models = task.get("models")
        try:
            # Build comprehensive prompt
            specialist_prompt = self.build_prompt(task_str, context, user_context)

            # Determine model order (allows dynamic routing)
            model_order = models or self.preferred_models

            # Try models in order
            for model in model_order:
                try:
                    response = await self._generate_response(model, specialist_prompt)

                    # Process and analyze the response
                    result = self.process_model_response(response, model, task_str)

                    return result

                except Exception as e:
                    logger.warning(f"{self.specialization} agent failed with {model}: {e}")
                    continue

            # If all models failed
            raise Exception(f"All models failed for {self.specialization} agent")

        except Exception as e:
            logger.error(f"Task processing failed for {self.specialization}: {e}")
            return self._create_error_result(str(e), task_str)

    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from feedback and adapt behavior"""
        logger.info(f"[{self.agent_id}] Received feedback: {feedback}")
        # Placeholder for learning logic
        return True
    
    def build_prompt(
        self, task: str, context: List[Dict] = None, user_context: str = None
    ) -> str:
        """Build comprehensive prompt for specialist analysis"""
        
        prompt_parts = [
            self.expertise_prompt,
            "\n" + "="*50 + "\n"
        ]
        
        # Add context from other specialists if available
        if context:
            prompt_parts.append("**CONTEXT FROM OTHER SPECIALISTS:**")
            for ctx in context:
                specialist = ctx.get("specialist", "unknown")
                insights = ctx.get("key_points", [])
                confidence = ctx.get("confidence", 0.0)
                
                prompt_parts.append(f"\n{specialist.title()} Expert (confidence: {confidence:.2f}):")
                if isinstance(insights, list):
                    for insight in insights:
                        prompt_parts.append(f"  • {insight}")
                else:
                    prompt_parts.append(f"  • {insights}")
            prompt_parts.append("\n" + "-"*30 + "\n")
        
        # Add user context if provided
        if user_context:
            prompt_parts.append("**ADDITIONAL CONTEXT:**")
            prompt_parts.append(user_context)
            prompt_parts.append("\n" + "-"*30 + "\n")
        
        # Add the main task
        prompt_parts.extend([
            f"**YOUR SPECIALIST TASK:**",
            task,
            "\n" + "-"*30 + "\n",
            f"**INSTRUCTIONS:**",
            f"As a {self.specialization} expert, provide detailed analysis from your specialized perspective.",
            "Structure your response with clear sections and actionable recommendations.",
            "Include confidence levels for your recommendations where appropriate.",
            "Focus on your area of expertise while considering insights from other specialists."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_response(self, model: str, prompt: str) -> str:
        """Generate response using specified model"""
        server = self._get_server_for_model(model)

        if not server:
            raise Exception(f"No server available for model: {model}")

        response = await self.mcp_client.generate_response(
            server=server,
            model=model,
            prompt=prompt,
        )

        return response

    def process_model_response(self, response: str, model: str, task: str) -> Dict[str, Any]:
        """Process model output and update history."""
        result = self._process_response(response, model, task)
        self.task_history.append(
            {
                "task": task,
                "response": response,
                "model_used": model,
                "timestamp": datetime.now().isoformat(),
                "confidence": result["confidence"],
            }
        )
        return result
    
    def _get_server_for_model(self, model: str) -> Optional[str]:
        """Determine which server hosts a given model"""
        model_servers = {
            "llama3.2": "ollama",
            "llama3.1": "ollama", 
            "llama3": "ollama",
            "codellama": "ollama",
            "qwen2.5-coder": "ollama",
            "gpt-4": "openai",
            "gpt-3.5-turbo": "openai",
            "claude-3.5-sonnet": "anthropic",
            "claude-3": "anthropic",
            "gemini-pro": "google"
        }
        
        return model_servers.get(model, "ollama")  # Default to ollama
    
    def _process_response(self, response: str, model: str, task: str) -> Dict[str, Any]:
        """Process and analyze the specialist response"""
        
        # Extract key insights and recommendations
        suggestions = self._extract_suggestions(response)
        confidence = self._assess_confidence(response, model)
        priority_issues = self._extract_priority_issues(response)
        
        return {
            "specialist": self.specialization,
            "model_used": model,
            "response": response,
            "confidence": confidence,
            "suggestions": suggestions,
            "priority_issues": priority_issues,
            "timestamp": datetime.now().isoformat(),
            "task_summary": task[:100] + "..." if len(task) > 100 else task
        }
    
    def _assess_confidence(self, response: str, model: str) -> float:
        """Assess confidence in the response based on various factors"""
        confidence = 0.5  # Base confidence
        
        # Model-based confidence adjustment
        model_confidence = {
            "claude-3.5-sonnet": 0.9,
            "gpt-4": 0.9,
            "gpt-3.5-turbo": 0.7,
            "llama3.2": 0.7,
            "codellama": 0.8,  # Higher for code-related tasks
            "qwen2.5-coder": 0.8
        }
        
        confidence = model_confidence.get(model, 0.6)
        
        # Response quality indicators
        if len(response) > 200:  # Detailed response
            confidence += 0.1
        
        if any(word in response.lower() for word in ["recommend", "suggest", "should", "consider"]):
            confidence += 0.05  # Actionable advice
        
        if any(word in response.lower() for word in ["critical", "security", "important", "risk"]):
            confidence += 0.05  # Identifies important issues
        
        # Specialty-specific confidence adjustments
        if self.specialization == "code_review" and "def " in response:
            confidence += 0.1  # Contains code examples
        
        if self.specialization == "security" and any(word in response.lower() for word in ["vulnerability", "attack", "exploit"]):
            confidence += 0.1  # Security-focused content
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract actionable suggestions from response"""
        suggestions = []
        
        # Look for common suggestion patterns
        patterns = [
            r"(?:recommend|suggest|should|consider|try)\s+(.+?)(?:\.|$)",
            r"•\s*(.+?)(?:\n|$)",
            r"\d+\.\s*(.+?)(?:\n|$)",
            r"-\s*(.+?)(?:\n|$)"
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
            suggestions.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        # Remove duplicates and limit to top 10
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions and len(suggestion) > 10:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:10]
    
    def _extract_priority_issues(self, response: str) -> List[Dict[str, str]]:
        """Extract and categorize priority issues"""
        issues = []
        
        # Look for severity indicators
        critical_keywords = ["critical", "severe", "urgent", "immediate", "security"]
        high_keywords = ["important", "significant", "major", "risk"]
        medium_keywords = ["minor", "consider", "recommend", "improve"]
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) < 20:  # Skip short lines
                continue
                
            severity = "low"
            if any(keyword in line.lower() for keyword in critical_keywords):
                severity = "critical"
            elif any(keyword in line.lower() for keyword in high_keywords):
                severity = "high"
            elif any(keyword in line.lower() for keyword in medium_keywords):
                severity = "medium"
            
            if severity != "low":
                issues.append({
                    "description": line,
                    "severity": severity,
                    "category": self.specialization
                })
        
        return issues[:5]  # Limit to top 5 issues
    
    def _create_error_result(self, error_msg: str, task: str) -> Dict[str, Any]:
        """Create error result when processing fails"""
        return {
            "specialist": self.specialization,
            "model_used": "none",
            "response": f"I apologize, but I encountered an error while analyzing this {self.specialization} task: {error_msg}",
            "confidence": 0.0,
            "suggestions": [],
            "priority_issues": [],
            "error": True,
            "timestamp": datetime.now().isoformat(),
            "task_summary": task[:100] + "..." if len(task) > 100 else task
        }
    
    def get_specialization_info(self) -> Dict[str, Any]:
        """Get information about this specialist"""
        return {
            "specialization": self.specialization,
            "preferred_models": self.preferred_models,
            "tasks_completed": len(self.task_history),
            "average_confidence": self._calculate_average_confidence(),
            "expertise_areas": self._get_expertise_areas()
        }
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all tasks"""
        if not self.task_history:
            return 0.0
        
        confidences = [task.get("confidence", 0.0) for task in self.task_history]
        return sum(confidences) / len(confidences)
    
    def _get_expertise_areas(self) -> List[str]:
        """Get list of expertise areas for this specialist"""
        expertise_map = {
            "code_review": ["Code Quality", "Best Practices", "Security", "Performance", "Testing"],
            "security": ["Vulnerability Assessment", "Secure Development", "Compliance", "Threat Analysis"],
            "architecture": ["System Design", "Scalability", "Technology Stack", "Quality Attributes"],
            "testing": ["Test Strategy", "Test Design", "Quality Metrics", "Continuous Quality"],
            "devops": ["Infrastructure as Code", "CI/CD", "Monitoring", "Operational Excellence"],

            "documentation": ["User Guides", "API Docs", "Tutorials", "Release Notes"],
            "database": ["Schema Design", "Query Optimization", "Migrations", "Performance"],
            "localization": ["Translation", "Internationalization", "Automation", "Cultural Adaptation"],
            "ethical_hacking": ["Penetration Testing", "Exploit Development", "Risk Reporting"],
            "cloud_cost": ["Usage Analysis", "Rightsizing", "Budget Forecasting", "Cost Monitoring"],
            "user_feedback": ["Sentiment Analysis", "Feature Requests", "Issue Categorization", "Task Prioritization"],
        }
        
        return expertise_map.get(self.specialization, ["General Analysis"])
    
    async def self_evaluate(self, task: str, response: str) -> Dict[str, Any]:
        """Self-evaluate the quality of a response"""
        evaluation_prompt = f"""
        As a {self.specialization} expert, evaluate the quality of this response:
        
        **Original Task:** {task}
        
        **Response to Evaluate:** {response}
        
        **Evaluation Criteria:**
        1. Accuracy and correctness
        2. Completeness and thoroughness  
        3. Practical applicability
        4. Clarity and structure
        
        Provide a brief evaluation with a confidence score (0.0-1.0).
        """
        
        try:
            model = self.preferred_models[0]  # Use best model for evaluation
            evaluation = await self._generate_response(model, evaluation_prompt)
            
            # Extract confidence score (simple implementation)
            import re
            confidence_match = re.search(r'(\d+\.?\d*)', evaluation)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.7
            
            return {
                "evaluation": evaluation,
                "self_confidence": min(confidence, 1.0),
                "evaluator": f"{self.specialization}_self_eval"
            }
            
        except Exception as e:
            return {
                "evaluation": f"Self-evaluation failed: {e}",
                "self_confidence": 0.5,
                "evaluator": f"{self.specialization}_self_eval"
            }
