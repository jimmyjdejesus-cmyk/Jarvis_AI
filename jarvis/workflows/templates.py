"""
🚀 PHASE 4: WORKFLOW TEMPLATES

Pre-built workflow patterns for common development and analysis scenarios.
These templates can be customized and reused across different projects.
"""

from typing import Dict, Any, List, Optional
from .engine import (
    Workflow, WorkflowContext, create_workflow, 
    add_specialist_task, add_custom_task
)
import os
import json

class WorkflowTemplates:
    """Collection of pre-built workflow templates"""
    
    @staticmethod
    def code_review_pipeline(file_path: str, 
                           review_criteria: List[str] = None) -> Workflow:
        """
        Complete code review pipeline:
        1. Security analysis
        2. Code quality review
        3. Testing recommendations
        4. Architecture assessment
        5. Final report generation
        """
        workflow = create_workflow(
            name="Code Review Pipeline",
            description=f"Complete code review for {file_path}",
            max_parallel=2
        )
        
        # Set initial context
        workflow.context.set_variable("file_path", file_path)
        workflow.context.set_variable("review_criteria", review_criteria or [])
        
        # 1. Security Analysis
        add_specialist_task(
            workflow,
            task_id="security_analysis",
            name="Security Analysis",
            specialist_type="security",
            prompt=f"""
Perform a comprehensive security analysis of the code in {file_path}.

Look for:
- Authentication and authorization vulnerabilities
- Input validation issues
- SQL injection risks
- XSS vulnerabilities
- Insecure data handling
- Cryptographic weaknesses
- Configuration security issues

Provide specific recommendations for each issue found.
"""
        )
        
        # 2. Code Quality Review (parallel with security)
        add_specialist_task(
            workflow,
            task_id="code_quality",
            name="Code Quality Review",
            specialist_type="code_review",
            prompt=f"""
Review the code quality of {file_path}.

Analyze:
- Code structure and organization
- Naming conventions
- Code complexity
- Performance considerations
- Best practices adherence
- Maintainability
- Documentation quality

Provide actionable improvement suggestions.
"""
        )
        
        # 3. Testing Strategy (depends on both security and quality)
        add_specialist_task(
            workflow,
            task_id="testing_strategy",
            name="Testing Strategy",
            specialist_type="testing",
            prompt=f"""
Based on the security analysis and code quality review, develop a comprehensive testing strategy for {file_path}.

Consider:
- Unit testing recommendations
- Integration testing needs
- Security testing requirements
- Performance testing considerations
- Test coverage goals

Previous analysis results:
Security findings: {{security_analysis.output}}
Quality findings: {{code_quality.output}}

Provide a detailed testing plan.
""",
            dependencies=["security_analysis", "code_quality"]
        )
        
        # 4. Architecture Assessment
        add_specialist_task(
            workflow,
            task_id="architecture_review",
            name="Architecture Assessment",
            specialist_type="architecture",
            prompt=f"""
Assess the architectural aspects of {file_path}.

Evaluate:
- Design patterns usage
- Scalability considerations
- Integration patterns
- Dependency management
- System boundaries
- Future extensibility

Consider the findings from:
Security: {{security_analysis.output}}
Code Quality: {{code_quality.output}}
Testing: {{testing_strategy.output}}

Provide architectural recommendations.
""",
            dependencies=["security_analysis", "code_quality", "testing_strategy"]
        )
        
        # 5. Final Report Generation
        add_custom_task(
            workflow,
            task_id="generate_report",
            name="Generate Final Report",
            function=lambda ctx: WorkflowTemplates._generate_code_review_report(ctx),
            dependencies=["security_analysis", "code_quality", "testing_strategy", "architecture_review"]
        )
        
        return workflow
    
    @staticmethod
    def deployment_pipeline(project_path: str, 
                          environment: str = "production",
                          deployment_config: Dict[str, Any] = None) -> Workflow:
        """
        Complete deployment pipeline:
        1. Pre-deployment security check
        2. Code quality validation
        3. Test execution
        4. Infrastructure assessment
        5. Deployment strategy
        6. Post-deployment monitoring setup
        """
        workflow = create_workflow(
            name="Deployment Pipeline",
            description=f"Deploy {project_path} to {environment}",
            max_parallel=3
        )
        
        # Set context
        workflow.context.set_variable("project_path", project_path)
        workflow.context.set_variable("environment", environment)
        workflow.context.set_variable("deployment_config", deployment_config or {})
        
        # 1. Pre-deployment Security Validation
        add_specialist_task(
            workflow,
            task_id="security_validation",
            name="Security Validation",
            specialist_type="security",
            prompt=f"""
Perform pre-deployment security validation for {project_path} targeting {environment} environment.

Check for:
- Production security configurations
- Secrets management
- Access controls
- Network security
- Data protection compliance
- Logging and monitoring security

Ensure the application is secure for {environment} deployment.
"""
        )
        
        # 2. Code Quality Gate
        add_specialist_task(
            workflow,
            task_id="quality_gate",
            name="Code Quality Gate",
            specialist_type="code_review",
            prompt=f"""
Validate code quality for production deployment of {project_path}.

Verify:
- Production readiness
- Error handling
- Performance optimization
- Resource management
- Code maintainability
- Documentation completeness

Confirm the code meets production quality standards.
"""
        )
        
        # 3. Test Validation
        add_specialist_task(
            workflow,
            task_id="test_validation",
            name="Test Validation",
            specialist_type="testing",
            prompt=f"""
Validate testing completeness for {project_path} deployment.

Ensure:
- All critical paths are tested
- Performance tests are passing
- Security tests are complete
- Integration tests are successful
- Regression tests are clean

Provide test readiness assessment for {environment} deployment.
"""
        )
        
        # 4. Infrastructure Assessment
        add_specialist_task(
            workflow,
            task_id="infrastructure_assessment",
            name="Infrastructure Assessment",
            specialist_type="devops",
            prompt=f"""
Assess infrastructure readiness for deploying {project_path} to {environment}.

Evaluate:
- Server capacity and scaling
- Database performance
- Network configuration
- Monitoring and alerting
- Backup and recovery
- Load balancing
- Security infrastructure

Configuration: {{deployment_config}}

Provide infrastructure recommendations and deployment strategy.
""",
            dependencies=["security_validation", "quality_gate", "test_validation"]
        )
        
        # 5. Deployment Execution Plan
        add_custom_task(
            workflow,
            task_id="deployment_plan",
            name="Create Deployment Plan",
            function=lambda ctx: WorkflowTemplates._create_deployment_plan(ctx),
            dependencies=["infrastructure_assessment"]
        )
        
        # 6. Monitoring Setup
        add_specialist_task(
            workflow,
            task_id="monitoring_setup",
            name="Post-Deployment Monitoring",
            specialist_type="devops",
            prompt=f"""
Design post-deployment monitoring and alerting for {project_path} in {environment}.

Set up:
- Application performance monitoring
- Error tracking and alerting
- Resource utilization monitoring
- Security event monitoring
- User experience tracking
- Business metric tracking

Based on deployment plan: {{deployment_plan.output}}

Provide comprehensive monitoring strategy.
""",
            dependencies=["deployment_plan"]
        )
        
        return workflow
    
    @staticmethod
    def project_analysis_workflow(project_path: str,
                                analysis_depth: str = "comprehensive") -> Workflow:
        """
        Complete project analysis workflow:
        1. Project structure analysis
        2. Security assessment
        3. Code quality analysis
        4. Architecture review
        5. Testing coverage analysis
        6. DevOps readiness assessment
        7. Comprehensive report
        """
        workflow = create_workflow(
            name="Project Analysis",
            description=f"Comprehensive analysis of {project_path}",
            max_parallel=3
        )
        
        # Set context
        workflow.context.set_variable("project_path", project_path)
        workflow.context.set_variable("analysis_depth", analysis_depth)
        
        # 1. Project Structure Analysis
        add_custom_task(
            workflow,
            task_id="project_structure",
            name="Analyze Project Structure",
            function=lambda ctx: WorkflowTemplates._analyze_project_structure(ctx)
        )
        
        # 2. Security Assessment
        add_specialist_task(
            workflow,
            task_id="security_assessment",
            name="Security Assessment",
            specialist_type="security",
            prompt=f"""
Perform comprehensive security assessment of {project_path}.

Analyze:
- Authentication mechanisms
- Authorization controls
- Data protection
- Input validation
- Output encoding
- Session management
- Cryptographic implementation
- Configuration security
- Dependency vulnerabilities

Project structure: {{project_structure.output}}

Provide detailed security findings and recommendations.
""",
            dependencies=["project_structure"]
        )
        
        # 3. Code Quality Analysis
        add_specialist_task(
            workflow,
            task_id="quality_analysis",
            name="Code Quality Analysis",
            specialist_type="code_review",
            prompt=f"""
Analyze code quality across {project_path}.

Evaluate:
- Code organization and structure
- Naming conventions and clarity
- Function and class design
- Code complexity and maintainability
- Performance considerations
- Error handling patterns
- Documentation quality
- Best practices adherence

Project structure: {{project_structure.output}}

Provide comprehensive quality assessment.
""",
            dependencies=["project_structure"]
        )
        
        # 4. Architecture Review
        add_specialist_task(
            workflow,
            task_id="architecture_analysis",
            name="Architecture Analysis",
            specialist_type="architecture",
            prompt=f"""
Review the architectural design of {project_path}.

Assess:
- Overall system architecture
- Design patterns and principles
- Component relationships
- Data flow and processing
- Scalability considerations
- Integration patterns
- Technology stack appropriateness
- Future extensibility

Project structure: {{project_structure.output}}
Security findings: {{security_assessment.output}}
Quality analysis: {{quality_analysis.output}}

Provide architectural insights and recommendations.
""",
            dependencies=["project_structure", "security_assessment", "quality_analysis"]
        )
        
        # 5. Testing Analysis
        add_specialist_task(
            workflow,
            task_id="testing_analysis",
            name="Testing Coverage Analysis",
            specialist_type="testing",
            prompt=f"""
Analyze testing coverage and strategy for {project_path}.

Evaluate:
- Existing test coverage
- Test quality and effectiveness
- Testing strategy completeness
- Performance testing
- Security testing
- Integration testing
- Test automation level

Project insights:
Structure: {{project_structure.output}}
Security: {{security_assessment.output}}
Quality: {{quality_analysis.output}}
Architecture: {{architecture_analysis.output}}

Provide testing recommendations and improvement plan.
""",
            dependencies=["project_structure", "security_assessment", "quality_analysis", "architecture_analysis"]
        )
        
        # 6. DevOps Assessment
        add_specialist_task(
            workflow,
            task_id="devops_assessment",
            name="DevOps Readiness Assessment",
            specialist_type="devops",
            prompt=f"""
Assess DevOps readiness and deployment capabilities for {project_path}.

Evaluate:
- CI/CD pipeline readiness
- Infrastructure as Code
- Monitoring and logging
- Deployment strategies
- Environment management
- Scaling capabilities
- Backup and recovery
- Security in deployment

Based on all previous analysis:
Structure: {{project_structure.output}}
Security: {{security_assessment.output}}
Quality: {{quality_analysis.output}}
Architecture: {{architecture_analysis.output}}
Testing: {{testing_analysis.output}}

Provide DevOps recommendations and deployment roadmap.
""",
            dependencies=["project_structure", "security_assessment", "quality_analysis", "architecture_analysis", "testing_analysis"]
        )
        
        # 7. Comprehensive Report
        add_custom_task(
            workflow,
            task_id="final_report",
            name="Generate Comprehensive Report",
            function=lambda ctx: WorkflowTemplates._generate_project_analysis_report(ctx),
            dependencies=["devops_assessment"]
        )
        
        return workflow
    
    @staticmethod
    def bug_fix_workflow(issue_description: str,
                        code_files: List[str] = None,
                        priority: str = "medium") -> Workflow:
        """
        Automated bug fix workflow:
        1. Issue analysis and understanding
        2. Root cause investigation
        3. Solution design
        4. Implementation planning
        5. Testing strategy
        6. Fix validation
        """
        workflow = create_workflow(
            name="Bug Fix Workflow",
            description=f"Fix issue: {issue_description[:100]}...",
            max_parallel=2
        )
        
        # Set context
        workflow.context.set_variable("issue_description", issue_description)
        workflow.context.set_variable("code_files", code_files or [])
        workflow.context.set_variable("priority", priority)
        
        # 1. Issue Analysis
        add_specialist_task(
            workflow,
            task_id="issue_analysis",
            name="Issue Analysis",
            specialist_type="code_review",
            prompt=f"""
Analyze the following issue in detail:

Issue: {issue_description}
Related files: {code_files or 'Not specified'}
Priority: {priority}

Provide:
1. Understanding of the problem
2. Potential impact assessment
3. Affected system components
4. Initial hypothesis about the cause
5. Information needed for investigation
"""
        )
        
        # 2. Root Cause Investigation
        add_specialist_task(
            workflow,
            task_id="root_cause_analysis",
            name="Root Cause Investigation",
            specialist_type="security" if "security" in issue_description.lower() else "code_review",
            prompt=f"""
Investigate the root cause of the issue based on initial analysis.

Issue details: {{issue_analysis.output}}

Perform:
1. Deep code analysis of relevant areas
2. Trace the problem through the system
3. Identify the exact cause
4. Assess any security implications
5. Determine scope of the fix needed

Provide detailed root cause analysis.
""",
            dependencies=["issue_analysis"]
        )
        
        # 3. Solution Design
        add_specialist_task(
            workflow,
            task_id="solution_design",
            name="Solution Design",
            specialist_type="architecture",
            prompt=f"""
Design a solution for the identified issue.

Issue analysis: {{issue_analysis.output}}
Root cause: {{root_cause_analysis.output}}

Design:
1. Optimal solution approach
2. Alternative solutions considered
3. Implementation strategy
4. Impact on existing code
5. Risk assessment
6. Rollback plan

Provide comprehensive solution design.
""",
            dependencies=["root_cause_analysis"]
        )
        
        # 4. Implementation Planning
        add_custom_task(
            workflow,
            task_id="implementation_plan",
            name="Create Implementation Plan",
            function=lambda ctx: WorkflowTemplates._create_implementation_plan(ctx),
            dependencies=["solution_design"]
        )
        
        # 5. Testing Strategy
        add_specialist_task(
            workflow,
            task_id="testing_strategy",
            name="Testing Strategy",
            specialist_type="testing",
            prompt=f"""
Develop comprehensive testing strategy for the bug fix.

Solution design: {{solution_design.output}}
Implementation plan: {{implementation_plan.output}}

Create:
1. Test cases to verify the fix
2. Regression test plan
3. Performance impact testing
4. Security testing (if applicable)
5. Integration testing requirements
6. User acceptance criteria

Provide detailed testing strategy.
""",
            dependencies=["implementation_plan"]
        )
        
        # 6. Final Validation Plan
        add_custom_task(
            workflow,
            task_id="validation_plan",
            name="Create Validation Plan",
            function=lambda ctx: WorkflowTemplates._create_validation_plan(ctx),
            dependencies=["testing_strategy"]
        )
        
        return workflow
    
    # Helper functions for custom tasks
    @staticmethod
    def _generate_code_review_report(context: WorkflowContext) -> str:
        """Generate comprehensive code review report"""
        security_result = context.get_output("security_analysis")
        quality_result = context.get_output("code_quality")
        testing_result = context.get_output("testing_strategy")
        architecture_result = context.get_output("architecture_review")
        
        report = f"""
# Code Review Report

**File:** {context.get_variable('file_path')}
**Generated:** {context.metadata.get('timestamp', 'Unknown')}

## Executive Summary
This comprehensive code review analyzes security, quality, testing, and architectural aspects.

## Security Analysis
{security_result or 'No security analysis available'}

## Code Quality Assessment
{quality_result or 'No quality analysis available'}

## Testing Recommendations
{testing_result or 'No testing analysis available'}

## Architecture Review
{architecture_result or 'No architecture analysis available'}

## Overall Recommendations
1. Address all security vulnerabilities with high priority
2. Implement suggested code quality improvements
3. Follow the testing strategy for comprehensive coverage
4. Consider architectural recommendations for long-term maintainability

## Next Steps
- Prioritize security fixes
- Implement quality improvements
- Set up recommended testing
- Plan architectural enhancements
"""
        return report
    
    @staticmethod
    def _create_deployment_plan(context: WorkflowContext) -> str:
        """Create detailed deployment plan"""
        infrastructure = context.get_output("infrastructure_assessment")
        environment = context.get_variable("environment")
        
        plan = f"""
# Deployment Plan for {environment.upper()}

## Infrastructure Readiness
{infrastructure or 'Infrastructure assessment not available'}

## Deployment Steps
1. **Pre-deployment Checklist**
   - Security validation complete
   - Quality gates passed
   - Tests validated
   - Infrastructure ready

2. **Deployment Process**
   - Blue-green deployment strategy
   - Gradual traffic routing
   - Health checks at each stage
   - Rollback procedures ready

3. **Post-deployment Validation**
   - System health verification
   - Performance monitoring
   - Error rate tracking
   - User experience validation

## Risk Mitigation
- Automated rollback triggers
- Monitoring and alerting
- Emergency response procedures
"""
        return plan
    
    @staticmethod
    def _analyze_project_structure(context: WorkflowContext) -> str:
        """Analyze project structure and provide insights"""
        project_path = context.get_variable("project_path")
        
        # This would typically scan the actual project
        # For now, return a template analysis
        analysis = f"""
# Project Structure Analysis

**Project Path:** {project_path}

## Directory Structure
- Source code organization
- Configuration files
- Documentation structure
- Test directories
- Build and deployment files

## Technology Stack Detected
- Programming languages
- Frameworks and libraries
- Database technologies
- Infrastructure components

## Key Findings
- Well-organized codebase
- Standard project structure
- Appropriate separation of concerns
- Good documentation practices

## Recommendations
- Continue following current structure
- Consider additional automation
- Enhance documentation in specific areas
"""
        return analysis
    
    @staticmethod
    def _generate_project_analysis_report(context: WorkflowContext) -> str:
        """Generate comprehensive project analysis report"""
        project_path = context.get_variable("project_path")
        
        # Collect all analysis results
        structure = context.get_output("project_structure")
        security = context.get_output("security_assessment")
        quality = context.get_output("quality_analysis")
        architecture = context.get_output("architecture_analysis")
        testing = context.get_output("testing_analysis")
        devops = context.get_output("devops_assessment")
        
        report = f"""
# Comprehensive Project Analysis Report

**Project:** {project_path}
**Analysis Date:** {context.metadata.get('timestamp', 'Unknown')}

## Executive Summary
This report provides a comprehensive analysis across security, quality, architecture, testing, and DevOps dimensions.

## 1. Project Structure
{structure or 'Structure analysis not available'}

## 2. Security Assessment
{security or 'Security assessment not available'}

## 3. Code Quality Analysis
{quality or 'Quality analysis not available'}

## 4. Architecture Review
{architecture or 'Architecture analysis not available'}

## 5. Testing Analysis
{testing or 'Testing analysis not available'}

## 6. DevOps Readiness
{devops or 'DevOps assessment not available'}

## Strategic Recommendations
1. **Immediate Actions** - Critical security and quality issues
2. **Short-term Goals** - Testing improvements and code quality
3. **Medium-term Objectives** - Architectural enhancements
4. **Long-term Vision** - DevOps maturity and scalability

## Conclusion
Comprehensive assessment complete with actionable recommendations for project improvement.
"""
        return report
    
    @staticmethod
    def _create_implementation_plan(context: WorkflowContext) -> str:
        """Create detailed implementation plan for bug fix"""
        solution = context.get_output("solution_design")
        
        plan = f"""
# Implementation Plan

## Solution Overview
{solution or 'Solution design not available'}

## Implementation Steps
1. **Preparation**
   - Create feature branch
   - Set up development environment
   - Review solution design

2. **Code Changes**
   - Implement core fix
   - Update related components
   - Add necessary error handling

3. **Testing**
   - Unit tests for changes
   - Integration testing
   - Regression testing

4. **Documentation**
   - Update code comments
   - Modify user documentation
   - Update change log

## Timeline Estimate
- Implementation: 2-4 hours
- Testing: 1-2 hours
- Documentation: 1 hour
- Total: 4-7 hours

## Resources Needed
- Development environment
- Testing framework
- Code review tools
"""
        return plan
    
    @staticmethod
    def _create_validation_plan(context: WorkflowContext) -> str:
        """Create validation plan for bug fix"""
        testing_strategy = context.get_output("testing_strategy")
        
        plan = f"""
# Fix Validation Plan

## Testing Strategy
{testing_strategy or 'Testing strategy not available'}

## Validation Checklist
✅ **Functional Validation**
- Fix addresses the original issue
- No new functionality is broken
- Edge cases are handled

✅ **Quality Validation**
- Code follows style guidelines
- Performance is not degraded
- Security is not compromised

✅ **Integration Validation**
- System integration is intact
- External dependencies work correctly
- User workflows are unaffected

## Acceptance Criteria
- Original issue is resolved
- All tests pass
- Performance meets requirements
- Security scan shows no new issues
- Code review approved

## Sign-off Requirements
- Technical review
- QA validation
- Product owner approval
"""
        return plan

# Convenience functions for common workflow creation
def create_code_review_workflow(file_path: str) -> Workflow:
    """Quick function to create a code review workflow"""
    return WorkflowTemplates.code_review_pipeline(file_path)

def create_deployment_workflow(project_path: str, environment: str = "production") -> Workflow:
    """Quick function to create a deployment workflow"""
    return WorkflowTemplates.deployment_pipeline(project_path, environment)

def create_project_analysis_workflow(project_path: str) -> Workflow:
    """Quick function to create a project analysis workflow"""
    return WorkflowTemplates.project_analysis_workflow(project_path)

def create_bug_fix_workflow(issue_description: str, code_files: List[str] = None) -> Workflow:
    """Quick function to create a bug fix workflow"""
    return WorkflowTemplates.bug_fix_workflow(issue_description, code_files)
