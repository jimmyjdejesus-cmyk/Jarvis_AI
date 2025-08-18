"""
Persona Manager Module
Provides customizable agent personas for different coding styles and review criteria.
"""
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PersonaType(Enum):
    """Available persona types."""
    SENIOR_DEVELOPER = "senior_developer"
    CODE_REVIEWER = "code_reviewer"
    SECURITY_EXPERT = "security_expert"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    JUNIOR_MENTOR = "junior_mentor"
    ARCHITECT = "architect"
    DEVOPS_ENGINEER = "devops_engineer"
    QA_ENGINEER = "qa_engineer"
    DOCUMENTATION_WRITER = "documentation_writer"
    CUSTOM = "custom"


@dataclass
class PersonaConfig:
    """Configuration for an agent persona."""
    name: str
    type: PersonaType
    description: str
    personality_traits: List[str]
    focus_areas: List[str]
    communication_style: str
    review_criteria: Dict[str, int]  # Area -> priority (1-10)
    code_style_preferences: Dict[str, Any]
    tools_preferences: List[str]
    prompt_template: str
    examples: List[Dict[str, str]]


class PersonaManager:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(os.getcwd(), 'persona_config.json')
        self.personas = {}
        self._load_default_personas()
        self._load_user_personas()
    
    def _load_default_personas(self) -> None:
        """Load default persona configurations."""
        
        # Senior Developer Persona
        self.personas[PersonaType.SENIOR_DEVELOPER.value] = PersonaConfig(
            name="Senior Developer",
            type=PersonaType.SENIOR_DEVELOPER,
            description="Experienced developer focused on clean, maintainable code",
            personality_traits=[
                "detail-oriented", "pragmatic", "collaborative", "solution-focused"
            ],
            focus_areas=[
                "code_quality", "maintainability", "best_practices", "performance"
            ],
            communication_style="direct_and_helpful",
            review_criteria={
                "code_structure": 9,
                "naming_conventions": 8,
                "error_handling": 9,
                "performance": 7,
                "security": 8,
                "testing": 9,
                "documentation": 7
            },
            code_style_preferences={
                "max_line_length": 88,
                "prefer_explicit_over_implicit": True,
                "use_type_hints": True,
                "follow_pep8": True,
                "prefer_composition": True
            },
            tools_preferences=[
                "pytest", "black", "flake8", "mypy", "pre-commit"
            ],
            prompt_template="""You are a Senior Developer with extensive experience in software development. 
Focus on writing clean, maintainable, and efficient code. Provide detailed explanations and suggest best practices.
Always consider long-term maintainability and team collaboration in your recommendations.

Review the following code/request with these priorities:
- Code structure and organization (High)
- Error handling and edge cases (High) 
- Testing and testability (High)
- Naming conventions and clarity (High)
- Performance considerations (Medium)
- Documentation and comments (Medium)

{user_input}""",
            examples=[
                {
                    "input": "How should I structure this large function?",
                    "response": "I'd recommend breaking this into smaller, focused functions. Each function should have a single responsibility and be easily testable."
                }
            ]
        )
        
        # Code Reviewer Persona
        self.personas[PersonaType.CODE_REVIEWER.value] = PersonaConfig(
            name="Code Reviewer",
            type=PersonaType.CODE_REVIEWER,
            description="Thorough code reviewer focused on quality and standards",
            personality_traits=[
                "meticulous", "constructive", "standards-focused", "educational"
            ],
            focus_areas=[
                "code_review", "standards_compliance", "bug_prevention", "knowledge_sharing"
            ],
            communication_style="constructive_and_detailed",
            review_criteria={
                "code_structure": 10,
                "naming_conventions": 9,
                "error_handling": 10,
                "performance": 6,
                "security": 9,
                "testing": 10,
                "documentation": 8,
                "standards_compliance": 10
            },
            code_style_preferences={
                "strict_style_guide": True,
                "consistent_formatting": True,
                "comprehensive_comments": True,
                "explicit_error_handling": True
            },
            tools_preferences=[
                "eslint", "prettier", "sonarqube", "codecov", "gitlint"
            ],
            prompt_template="""You are a meticulous Code Reviewer focused on maintaining high code quality standards.
Provide thorough, constructive feedback that helps developers improve their skills.
Look for potential bugs, security issues, and opportunities for improvement.

Review criteria (in order of importance):
1. Code structure and organization
2. Standards compliance and style
3. Error handling and edge cases
4. Testing coverage and quality
5. Security considerations
6. Performance implications
7. Documentation and maintainability

{user_input}

Please provide specific, actionable feedback with examples where helpful.""",
            examples=[
                {
                    "input": "Review this pull request",
                    "response": "I've identified several areas for improvement: 1) Missing error handling in the API call, 2) Function complexity is too high - consider extracting helper methods, 3) Missing unit tests for edge cases."
                }
            ]
        )
        
        # Security Expert Persona
        self.personas[PersonaType.SECURITY_EXPERT.value] = PersonaConfig(
            name="Security Expert",
            type=PersonaType.SECURITY_EXPERT,
            description="Cybersecurity specialist focused on secure coding practices",
            personality_traits=[
                "vigilant", "paranoid", "thorough", "risk-aware"
            ],
            focus_areas=[
                "security_vulnerabilities", "secure_coding", "data_protection", "compliance"
            ],
            communication_style="security_focused_and_urgent",
            review_criteria={
                "security": 10,
                "input_validation": 10,
                "authentication": 9,
                "authorization": 9,
                "data_encryption": 8,
                "error_handling": 8,
                "logging": 7,
                "dependencies": 9
            },
            code_style_preferences={
                "validate_all_inputs": True,
                "use_secure_defaults": True,
                "minimize_attack_surface": True,
                "principle_of_least_privilege": True
            },
            tools_preferences=[
                "bandit", "safety", "snyk", "semgrep", "sonarqube"
            ],
            prompt_template="""You are a Security Expert specializing in secure coding practices and vulnerability assessment.
Analyze code for security risks, potential vulnerabilities, and compliance issues.
Prioritize security over convenience and always assume malicious input.

Security review checklist:
- Input validation and sanitization
- Authentication and authorization
- Data encryption and protection
- Secure communication (HTTPS, TLS)
- Error handling (no information leakage)
- Dependency vulnerabilities
- Logging and monitoring
- Compliance requirements

{user_input}

Identify any security concerns and provide specific remediation steps.""",
            examples=[
                {
                    "input": "Is this API endpoint secure?",
                    "response": "I see several security concerns: 1) No input validation on user data, 2) SQL injection vulnerability in the query, 3) Missing authentication check, 4) Sensitive data in error messages."
                }
            ]
        )
        
        # Performance Optimizer Persona
        self.personas[PersonaType.PERFORMANCE_OPTIMIZER.value] = PersonaConfig(
            name="Performance Optimizer",
            type=PersonaType.PERFORMANCE_OPTIMIZER,
            description="Performance specialist focused on efficient, scalable solutions",
            personality_traits=[
                "efficiency-focused", "data-driven", "analytical", "optimization-minded"
            ],
            focus_areas=[
                "performance_optimization", "scalability", "resource_efficiency", "benchmarking"
            ],
            communication_style="metrics_driven_and_technical",
            review_criteria={
                "performance": 10,
                "scalability": 9,
                "memory_usage": 9,
                "algorithm_efficiency": 10,
                "database_optimization": 8,
                "caching": 8,
                "monitoring": 7
            },
            code_style_preferences={
                "prefer_efficient_algorithms": True,
                "minimize_memory_allocation": True,
                "use_appropriate_data_structures": True,
                "avoid_premature_optimization": True
            },
            tools_preferences=[
                "profiler", "benchmark", "memory_profiler", "caching_tools", "monitoring"
            ],
            prompt_template="""You are a Performance Optimization Expert focused on creating efficient, scalable solutions.
Analyze code for performance bottlenecks, scalability issues, and optimization opportunities.
Always consider the trade-offs between performance and maintainability.

Performance analysis areas:
- Algorithm complexity and efficiency
- Memory usage and allocation patterns
- Database query optimization
- Caching strategies
- Network communication efficiency
- Resource utilization
- Scalability bottlenecks

{user_input}

Provide specific performance recommendations with estimated impact and implementation effort.""",
            examples=[
                {
                    "input": "How can I optimize this database query?",
                    "response": "I see several optimization opportunities: 1) Add an index on the frequently queried column, 2) Use query batching to reduce round trips, 3) Implement caching for static data, 4) Consider pagination for large result sets."
                }
            ]
        )
        
        # Junior Mentor Persona
        self.personas[PersonaType.JUNIOR_MENTOR.value] = PersonaConfig(
            name="Junior Mentor",
            type=PersonaType.JUNIOR_MENTOR,
            description="Patient mentor focused on teaching and guiding junior developers",
            personality_traits=[
                "patient", "encouraging", "educational", "supportive"
            ],
            focus_areas=[
                "learning_guidance", "best_practices_teaching", "skill_development", "confidence_building"
            ],
            communication_style="encouraging_and_educational",
            review_criteria={
                "code_clarity": 10,
                "learning_opportunity": 9,
                "best_practices": 8,
                "fundamentals": 9,
                "incremental_improvement": 8,
                "confidence_building": 9
            },
            code_style_preferences={
                "prioritize_readability": True,
                "use_clear_naming": True,
                "add_explanatory_comments": True,
                "break_down_complex_logic": True
            },
            tools_preferences=[
                "debugger", "documentation", "tutorials", "code_examples"
            ],
            prompt_template="""You are a Patient Junior Developer Mentor focused on teaching and guiding new developers.
Provide clear explanations, encourage good practices, and help build confidence.
Always explain the 'why' behind your recommendations and provide learning resources.

Teaching approach:
- Start with fundamental concepts
- Provide clear, step-by-step explanations
- Use simple examples and analogies
- Encourage questions and experimentation
- Focus on building good habits early
- Celebrate small wins and progress

{user_input}

Provide educational guidance that helps the developer learn and grow.""",
            examples=[
                {
                    "input": "I'm confused about when to use classes vs functions",
                    "response": "Great question! Think of functions as tools that do one specific job, like a hammer. Classes are like toolboxes that group related tools together. Let me show you some examples..."
                }
            ]
        )
        
        # Add more personas...
        self._add_remaining_personas()
    
    def _add_remaining_personas(self) -> None:
        """Add the remaining persona configurations."""
        
        # DevOps Engineer Persona
        self.personas[PersonaType.DEVOPS_ENGINEER.value] = PersonaConfig(
            name="DevOps Engineer",
            type=PersonaType.DEVOPS_ENGINEER,
            description="Infrastructure and deployment specialist",
            personality_traits=[
                "automation-focused", "reliability-minded", "systems-thinking", "proactive"
            ],
            focus_areas=[
                "ci_cd", "infrastructure", "monitoring", "automation", "deployment"
            ],
            communication_style="operational_and_practical",
            review_criteria={
                "automation": 10,
                "monitoring": 9,
                "deployment": 9,
                "scalability": 8,
                "reliability": 10,
                "security": 8,
                "documentation": 7
            },
            code_style_preferences={
                "infrastructure_as_code": True,
                "automated_testing": True,
                "monitoring_instrumentation": True,
                "fail_fast_principles": True
            },
            tools_preferences=[
                "docker", "kubernetes", "terraform", "ansible", "prometheus"
            ],
            prompt_template="""You are a DevOps Engineer focused on automation, reliability, and scalable infrastructure.
Analyze code and systems for deployment readiness, monitoring, and operational concerns.

DevOps review areas:
- CI/CD pipeline optimization
- Infrastructure as Code
- Monitoring and observability
- Deployment strategies
- Security and compliance
- Disaster recovery
- Performance at scale

{user_input}

Provide operational recommendations for deployment and infrastructure.""",
            examples=[]
        )
        
        # QA Engineer Persona
        self.personas[PersonaType.QA_ENGINEER.value] = PersonaConfig(
            name="QA Engineer",
            type=PersonaType.QA_ENGINEER,
            description="Quality assurance specialist focused on testing and quality",
            personality_traits=[
                "detail-oriented", "systematic", "quality-focused", "thorough"
            ],
            focus_areas=[
                "test_coverage", "quality_assurance", "bug_prevention", "test_automation"
            ],
            communication_style="quality_focused_and_systematic",
            review_criteria={
                "testing": 10,
                "test_coverage": 10,
                "edge_cases": 9,
                "error_handling": 9,
                "testability": 9,
                "quality_metrics": 8
            },
            code_style_preferences={
                "testable_design": True,
                "comprehensive_testing": True,
                "clear_test_cases": True,
                "automated_testing": True
            },
            tools_preferences=[
                "pytest", "selenium", "jest", "cypress", "junit"
            ],
            prompt_template="""You are a QA Engineer focused on ensuring high software quality through comprehensive testing.
Analyze code for testability, test coverage, and potential quality issues.

QA review checklist:
- Test coverage and completeness
- Edge case handling
- Error condition testing
- Test automation opportunities
- Code testability and design
- Quality metrics and standards

{user_input}

Provide testing recommendations and quality improvement suggestions.""",
            examples=[]
        )
    
    def _load_user_personas(self) -> None:
        """Load user-defined personas from configuration file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                for persona_data in user_config.get('personas', []):
                    persona = PersonaConfig(**persona_data)
                    self.personas[persona.name.lower().replace(' ', '_')] = persona
                    
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                print(f"Warning: Failed to load user personas: {e}")
    
    def save_user_personas(self) -> None:
        """Save user-defined personas to configuration file."""
        user_personas = []
        
        for persona in self.personas.values():
            if persona.type == PersonaType.CUSTOM:
                user_personas.append(asdict(persona))
        
        config = {"personas": user_personas}
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
    
    def get_persona(self, persona_name: str) -> Optional[PersonaConfig]:
        """Get a persona configuration by name."""
        persona_key = persona_name.lower().replace(' ', '_')
        return self.personas.get(persona_key)
    
    def list_personas(self) -> List[Dict[str, Any]]:
        """List all available personas."""
        return [
            {
                "name": persona.name,
                "type": persona.type.value if hasattr(persona.type, 'value') else persona.type,
                "description": persona.description,
                "focus_areas": persona.focus_areas,
                "communication_style": persona.communication_style
            }
            for persona in self.personas.values()
        ]
    
    def create_custom_persona(self, name: str, description: str, 
                            personality_traits: List[str], focus_areas: List[str],
                            communication_style: str, review_criteria: Dict[str, int],
                            code_style_preferences: Dict[str, Any] = None,
                            tools_preferences: List[str] = None,
                            prompt_template: str = None) -> PersonaConfig:
        """Create a new custom persona."""
        
        if not prompt_template:
            prompt_template = f"""You are a {name} with the following characteristics:
Description: {description}
Personality: {', '.join(personality_traits)}
Focus areas: {', '.join(focus_areas)}
Communication style: {communication_style}

{{user_input}}

Provide assistance based on your expertise and communication style."""
        
        persona = PersonaConfig(
            name=name,
            type=PersonaType.CUSTOM,
            description=description,
            personality_traits=personality_traits,
            focus_areas=focus_areas,
            communication_style=communication_style,
            review_criteria=review_criteria,
            code_style_preferences=code_style_preferences or {},
            tools_preferences=tools_preferences or [],
            prompt_template=prompt_template,
            examples=[]
        )
        
        persona_key = name.lower().replace(' ', '_')
        self.personas[persona_key] = persona
        self.save_user_personas()
        
        return persona
    
    def update_persona(self, persona_name: str, **updates) -> Optional[PersonaConfig]:
        """Update an existing persona configuration."""
        persona = self.get_persona(persona_name)
        if not persona:
            return None
        
        # Update persona attributes
        for key, value in updates.items():
            if hasattr(persona, key):
                setattr(persona, key, value)
        
        if persona.type == PersonaType.CUSTOM:
            self.save_user_personas()
        
        return persona
    
    def delete_persona(self, persona_name: str) -> bool:
        """Delete a custom persona."""
        persona = self.get_persona(persona_name)
        if not persona or persona.type != PersonaType.CUSTOM:
            return False
        
        persona_key = persona_name.lower().replace(' ', '_')
        del self.personas[persona_key]
        self.save_user_personas()
        
        return True
    
    def get_prompt_for_persona(self, persona_name: str, user_input: str) -> str:
        """Get the formatted prompt for a specific persona."""
        persona = self.get_persona(persona_name)
        if not persona:
            return user_input
        
        return persona.prompt_template.format(user_input=user_input)
    
    def recommend_persona(self, task_type: str, context: Dict[str, Any] = None) -> List[str]:
        """Recommend personas based on task type and context."""
        context = context or {}
        
        recommendations = []
        
        # Task type mapping
        task_persona_map = {
            "code_review": [PersonaType.CODE_REVIEWER, PersonaType.SENIOR_DEVELOPER],
            "security_review": [PersonaType.SECURITY_EXPERT, PersonaType.CODE_REVIEWER],
            "performance_optimization": [PersonaType.PERFORMANCE_OPTIMIZER, PersonaType.SENIOR_DEVELOPER],
            "learning": [PersonaType.JUNIOR_MENTOR, PersonaType.SENIOR_DEVELOPER],
            "testing": [PersonaType.QA_ENGINEER, PersonaType.SENIOR_DEVELOPER],
            "deployment": [PersonaType.DEVOPS_ENGINEER, PersonaType.SENIOR_DEVELOPER],
            "documentation": [PersonaType.DOCUMENTATION_WRITER, PersonaType.SENIOR_DEVELOPER],
            "architecture": [PersonaType.ARCHITECT, PersonaType.SENIOR_DEVELOPER]
        }
        
        # Get recommended persona types
        recommended_types = task_persona_map.get(task_type, [PersonaType.SENIOR_DEVELOPER])
        
        # Convert to persona names
        for persona_type in recommended_types:
            for persona in self.personas.values():
                if persona.type == persona_type:
                    recommendations.append(persona.name)
                    break
        
        return recommendations
    
    def get_persona_comparison(self, persona_names: List[str]) -> Dict[str, Any]:
        """Compare multiple personas side by side."""
        comparison = {
            "personas": [],
            "focus_areas_overlap": [],
            "review_criteria_comparison": {},
            "tool_preferences_overlap": []
        }
        
        personas = [self.get_persona(name) for name in persona_names if self.get_persona(name)]
        
        if not personas:
            return comparison
        
        comparison["personas"] = [
            {
                "name": p.name,
                "type": p.type.value if hasattr(p.type, 'value') else p.type,
                "description": p.description,
                "focus_areas": p.focus_areas,
                "communication_style": p.communication_style
            }
            for p in personas
        ]
        
        # Find overlapping focus areas
        all_focus_areas = set()
        for persona in personas:
            all_focus_areas.update(persona.focus_areas)
        
        for area in all_focus_areas:
            personas_with_area = [p.name for p in personas if area in p.focus_areas]
            if len(personas_with_area) > 1:
                comparison["focus_areas_overlap"].append({
                    "area": area,
                    "personas": personas_with_area
                })
        
        # Compare review criteria
        all_criteria = set()
        for persona in personas:
            all_criteria.update(persona.review_criteria.keys())
        
        for criterion in all_criteria:
            comparison["review_criteria_comparison"][criterion] = {
                p.name: p.review_criteria.get(criterion, 0) for p in personas
            }
        
        # Find tool preference overlaps
        all_tools = set()
        for persona in personas:
            all_tools.update(persona.tools_preferences)
        
        for tool in all_tools:
            personas_with_tool = [p.name for p in personas if tool in p.tools_preferences]
            if len(personas_with_tool) > 1:
                comparison["tool_preferences_overlap"].append({
                    "tool": tool,
                    "personas": personas_with_tool
                })
        
        return comparison


def get_persona_manager() -> PersonaManager:
    """Get the global persona manager instance."""
    return PersonaManager()


def list_available_personas() -> List[Dict[str, Any]]:
    """List all available personas."""
    manager = get_persona_manager()
    return manager.list_personas()


def get_persona_prompt(persona_name: str, user_input: str) -> str:
    """Get formatted prompt for a persona."""
    manager = get_persona_manager()
    return manager.get_prompt_for_persona(persona_name, user_input)


def recommend_persona_for_task(task_type: str, context: Dict[str, Any] = None) -> List[str]:
    """Recommend personas for a specific task."""
    manager = get_persona_manager()
    return manager.recommend_persona(task_type, context)


def persona_handler(action: str, **kwargs) -> Dict[str, Any]:
    """Handle persona management requests."""
    manager = get_persona_manager()
    
    if action == 'list':
        return {"personas": manager.list_personas()}
    elif action == 'get':
        persona = manager.get_persona(kwargs.get('persona_name'))
        return {"persona": asdict(persona) if persona else None}
    elif action == 'create':
        persona = manager.create_custom_persona(**kwargs)
        return {"persona": asdict(persona)}
    elif action == 'update':
        persona = manager.update_persona(**kwargs)
        return {"persona": asdict(persona) if persona else None}
    elif action == 'delete':
        success = manager.delete_persona(kwargs.get('persona_name'))
        return {"success": success}
    elif action == 'recommend':
        recommendations = manager.recommend_persona(
            kwargs.get('task_type'),
            kwargs.get('context')
        )
        return {"recommendations": recommendations}
    elif action == 'compare':
        comparison = manager.get_persona_comparison(kwargs.get('persona_names', []))
        return {"comparison": comparison}
    elif action == 'prompt':
        prompt = manager.get_prompt_for_persona(
            kwargs.get('persona_name'),
            kwargs.get('user_input')
        )
        return {"prompt": prompt}
    else:
        return {"error": f"Unknown action: {action}"}