"""
Specialized Agent Implementations
Each agent is an expert in their domain
"""
import ast
from typing import Dict, List

from .specialist import SpecialistAgent
from jarvis.world_model.knowledge_graph import KnowledgeGraph

class CodeReviewAgent(SpecialistAgent):
    """Expert code reviewer specializing in code quality and best practices"""

    def __init__(
        self,
        mcp_client,
        knowledge_graph: KnowledgeGraph | None = None,
    ):
        super().__init__(
            specialization="code_review",
            preferred_models=["claude-3.5-sonnet", "gpt-4", "codellama", "llama3.2"],
            mcp_client=mcp_client,
        )
        self.knowledge_graph = knowledge_graph

    def _dependencies_for_code(self, code: str) -> Dict[str, List[str]]:
        """Find function call dependencies using the world model."""

        if not self.knowledge_graph:
            return {}
        try:
            tree = ast.parse(code)
        except Exception:
            return {}

        deps: Dict[str, List[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_ids = self.knowledge_graph.find_functions(node.name)
                calls: List[str] = []
                for fid in func_ids:
                    calls.extend(self.knowledge_graph.get_function_dependencies(fid))
                if calls:
                    deps[node.name] = calls
        return deps

    async def review_code(self, code: str, language: str = None, context: str = None) -> dict:
        """
        Comprehensive code review with dependency analysis

        Args:
            code: Code to review
            language: Programming language (auto-detect if None)
            context: Additional context about the code

        Returns:
            Detailed code review results
        """
        deps = self._dependencies_for_code(code)
        dep_text = "\n".join(
            f"{func}: {', '.join(calls)}" for func, calls in deps.items()
        )
        dependency_section = (
            f"\n**Known Dependencies:**\n{dep_text}\n" if dep_text else ""
        )
        review_task = f"""
        **CODE REVIEW REQUEST**

        Programming Language: {language or 'Auto-detect'}

        **Code to Review:**
        ```
        {code}
        ```
        {dependency_section}
        **Additional Context:**
        {context or 'No additional context provided'}

        **Review Requirements:**
        1. Code quality and readability assessment
        2. Security vulnerability analysis
        3. Performance optimization opportunities
        4. Best practices compliance
        5. Potential bugs or edge cases
        6. Maintainability and extensibility
        7. Testing recommendations

        Please provide specific, actionable feedback with code examples where helpful.
        """

        return await self.process_task(review_task)
    
    async def suggest_improvements(self, code: str, focus_area: str = None) -> dict:
        """Suggest specific improvements for code"""
        improvement_task = f"""
        **CODE IMPROVEMENT REQUEST**
        
        Focus Area: {focus_area or 'General improvements'}
        
        **Code:**
        ```
        {code}
        ```
        
        Please suggest specific improvements with before/after examples.
        """
        
        return await self.process_task(improvement_task)

class SecurityAgent(SpecialistAgent):
    """Expert security analyst specializing in vulnerability assessment"""
    
    def __init__(self, mcp_client):
        super().__init__(
            specialization="security",
            preferred_models=["claude-3.5-sonnet", "gpt-4", "llama3.2"],
            mcp_client=mcp_client
        )
    
    async def security_audit(self, code: str = None, description: str = None) -> dict:
        """
        Comprehensive security audit
        
        Args:
            code: Code to audit (optional)
            description: System/feature description
            
        Returns:
            Security assessment results
        """
        audit_task = f"""
        **SECURITY AUDIT REQUEST**
        
        {'**Code to Audit:**' if code else '**System Description:**'}
        ```
        {code if code else description}
        ```
        
        **Security Assessment Requirements:**
        1. OWASP Top 10 vulnerability analysis
        2. Authentication and authorization review
        3. Input validation and sanitization
        4. Data protection and privacy assessment
        5. Cryptographic implementation review
        6. API security considerations
        7. Infrastructure security recommendations
        
        Provide specific vulnerability findings with risk levels and remediation steps.
        """
        
        return await self.process_task(audit_task)
    
    async def threat_modeling(self, system_description: str) -> dict:
        """Perform threat modeling analysis"""
        threat_task = f"""
        **THREAT MODELING REQUEST**
        
        **System Description:**
        {system_description}
        
        **Analysis Requirements:**
        1. Attack surface identification
        2. Threat actor analysis
        3. Attack vector mapping
        4. Risk assessment and prioritization
        5. Mitigation strategies
        6. Security controls recommendations
        
        Provide a comprehensive threat model with actionable security measures.
        """
        
        return await self.process_task(threat_task)

class ArchitectureAgent(SpecialistAgent):
    """Expert software architect specializing in system design"""
    
    def __init__(self, mcp_client):
        super().__init__(
            specialization="architecture",
            preferred_models=["gpt-4", "claude-3.5-sonnet", "llama3.2"],
            mcp_client=mcp_client
        )
    
    async def design_review(self, description: str, requirements: str = None) -> dict:
        """
        Architecture design review
        
        Args:
            description: System architecture description
            requirements: System requirements
            
        Returns:
            Architecture analysis and recommendations
        """
        design_task = f"""
        **ARCHITECTURE DESIGN REVIEW**
        
        **System Description:**
        {description}
        
        **Requirements:**
        {requirements or 'No specific requirements provided'}
        
        **Review Focus Areas:**
        1. Architectural patterns and design principles
        2. Scalability and performance considerations
        3. Technology stack evaluation
        4. Component coupling and cohesion
        5. Data architecture and storage strategy
        6. Integration patterns and API design
        7. Deployment and operational considerations
        8. Cost optimization opportunities
        
        Provide architectural recommendations with trade-off analysis.
        """
        
        return await self.process_task(design_task)
    
    async def technology_recommendation(self, project_description: str, constraints: str = None) -> dict:
        """Recommend technology stack for a project"""
        tech_task = f"""
        **TECHNOLOGY STACK RECOMMENDATION**
        
        **Project Description:**
        {project_description}
        
        **Constraints:**
        {constraints or 'No specific constraints'}
        
        **Recommendation Areas:**
        1. Programming languages and frameworks
        2. Database and storage solutions
        3. Cloud platform and services
        4. Development and deployment tools
        5. Monitoring and observability stack
        6. Security and compliance tools
        
        Provide justified technology recommendations with pros/cons analysis.
        """
        
        return await self.process_task(tech_task)

class TestingAgent(SpecialistAgent):
    """Expert testing specialist focusing on quality assurance"""
    
    def __init__(self, mcp_client):
        super().__init__(
            specialization="testing",
            preferred_models=["claude-3.5-sonnet", "gpt-4", "llama3.2"],
            mcp_client=mcp_client
        )
    
    async def testing_strategy(self, code: str = None, description: str = None) -> dict:
        """Develop comprehensive testing strategy"""
        strategy_task = f"""
        **TESTING STRATEGY DEVELOPMENT**
        
        {'**Code to Test:**' if code else '**System Description:**'}
        ```
        {code if code else description}
        ```
        
        **Testing Strategy Requirements:**
        1. Test pyramid implementation (unit, integration, e2e)
        2. Test case design and coverage goals
        3. Testing framework recommendations
        4. Test data management strategy
        5. Automated testing pipeline
        6. Performance and load testing approach
        7. Quality metrics and reporting
        
        Provide a comprehensive testing strategy with implementation guidance.
        """
        
        return await self.process_task(strategy_task)
    
    async def generate_test_cases(self, code: str, test_type: str = "unit") -> dict:
        """Generate specific test cases for code"""
        test_task = f"""
        **TEST CASE GENERATION**
        
        Test Type: {test_type}
        
        **Code to Test:**
        ```
        {code}
        ```
        
        **Requirements:**
        1. Generate comprehensive {test_type} test cases
        2. Include edge cases and error conditions
        3. Provide test data and expected outcomes
        4. Include setup and teardown requirements
        5. Consider boundary value analysis
        6. Include negative test scenarios
        
        Provide detailed test cases with executable code examples.
        """
        
        return await self.process_task(test_task)

class DevOpsAgent(SpecialistAgent):
    """Expert DevOps engineer specializing in automation and infrastructure"""
    
    def __init__(self, mcp_client):
        super().__init__(
            specialization="devops",
            preferred_models=["claude-3.5-sonnet", "gpt-4", "llama3.2"],
            mcp_client=mcp_client
        )
    
    async def infrastructure_review(self, description: str, requirements: str = None) -> dict:
        """Review infrastructure design and provide recommendations"""
        infra_task = f"""
        **INFRASTRUCTURE REVIEW**
        
        **Infrastructure Description:**
        {description}
        
        **Requirements:**
        {requirements or 'No specific requirements provided'}
        
        **Review Areas:**
        1. Infrastructure as Code (IaC) best practices
        2. Scalability and high availability design
        3. Security and compliance considerations
        4. Cost optimization opportunities
        5. Monitoring and observability setup
        6. Backup and disaster recovery strategy
        7. CI/CD pipeline optimization
        8. Container and orchestration strategy
        
        Provide infrastructure recommendations with implementation guidance.
        """
        
        return await self.process_task(infra_task)
    
    async def cicd_optimization(self, pipeline_description: str) -> dict:
        """Optimize CI/CD pipeline configuration"""
        cicd_task = f"""
        **CI/CD PIPELINE OPTIMIZATION**
        
        **Current Pipeline:**
        {pipeline_description}
        
        **Optimization Areas:**
        1. Build time optimization
        2. Pipeline security and compliance
        3. Deployment strategies (blue-green, canary)
        4. Testing integration and quality gates
        5. Artifact management and caching
        6. Environment promotion strategies
        7. Rollback and recovery procedures
        8. Monitoring and alerting integration
        
        Provide specific pipeline improvements with configuration examples.
        """
        
        return await self.process_task(cicd_task)
