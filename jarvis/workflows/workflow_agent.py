"""
🚀 PHASE 4: WORKFLOW-ENHANCED JARVIS AGENT

Enhanced Jarvis agent with advanced workflow orchestration capabilities,
intelligent task decomposition, and automated problem-solving workflows.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.enhanced_agent import EnhancedJarvisAgent
from .engine import WorkflowEngine, Workflow, WorkflowStatus
from .templates import WorkflowTemplates
from .integrations import IntegrationManager

logger = logging.getLogger(__name__)

class WorkflowJarvisAgent(EnhancedJarvisAgent):
    """
    Enhanced Jarvis agent with advanced workflow capabilities
    
    Adds intelligent workflow orchestration on top of multi-agent coordination:
    - Automatic workflow detection and creation
    - Complex task decomposition
    - Automated problem-solving pipelines
    - Integration with external tools and systems
    """
    
    def __init__(self, 
                 enable_mcp: bool = True,
                 enable_multi_agent: bool = True,
                 enable_workflows: bool = True):
        
        super().__init__(enable_mcp=enable_mcp, enable_multi_agent=enable_multi_agent)
        
        self.enable_workflows = enable_workflows
        self.workflow_engine = WorkflowEngine() if enable_workflows else None
        self.integration_manager = IntegrationManager() if enable_workflows else None
        
        # Workflow intelligence
        self.workflow_patterns = self._initialize_workflow_patterns()
        self.active_workflows: Dict[str, Workflow] = {}
        
        logger.info(f"WorkflowJarvisAgent initialized - Workflows: {enable_workflows}")
    
    def _initialize_workflow_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow detection patterns"""
        return {
            "code_review": {
                "keywords": ["review", "analyze", "check", "audit", "examine"],
                "code_indicators": ["file", "code", "function", "class", "script"],
                "template": "code_review_pipeline"
            },
            "deployment": {
                "keywords": ["deploy", "release", "publish", "launch"],
                "context_indicators": ["production", "staging", "environment"],
                "template": "deployment_pipeline"
            },
            "project_analysis": {
                "keywords": ["analyze", "assess", "evaluate", "review"],
                "scope_indicators": ["project", "application", "system", "codebase"],
                "template": "project_analysis_workflow"
            },
            "bug_fix": {
                "keywords": ["fix", "bug", "issue", "problem", "error"],
                "indicators": ["not working", "broken", "fails", "exception"],
                "template": "bug_fix_workflow"
            },
            "feature_development": {
                "keywords": ["implement", "add", "create", "build", "develop"],
                "indicators": ["feature", "functionality", "capability"],
                "template": "feature_development_workflow"
            }
        }
    
    async def chat_async(self, message: str, **kwargs) -> str:
        """
        Enhanced chat with workflow intelligence
        
        Analyzes the message to determine if a workflow should be triggered,
        then either executes a workflow or falls back to standard multi-agent processing.
        """
        
        # Analyze if this requires a workflow
        workflow_analysis = await self._analyze_for_workflow(message)
        
        if (self.enable_workflows and 
            workflow_analysis["requires_workflow"] and 
            workflow_analysis["confidence"] > 0.7):
            
            logger.info(f"Triggering workflow: {workflow_analysis['workflow_type']}")
            return await self._execute_workflow_response(message, workflow_analysis)
        
        else:
            # Fall back to standard multi-agent processing
            logger.info("Using standard multi-agent processing")
            return await super().chat_async(message, **kwargs)
    
    async def _analyze_for_workflow(self, message: str) -> Dict[str, Any]:
        """Analyze message to determine if a workflow is needed"""
        
        message_lower = message.lower()
        best_match = None
        best_confidence = 0.0
        
        for workflow_type, pattern in self.workflow_patterns.items():
            confidence = 0.0
            
            # Check for keywords
            keyword_matches = sum(1 for keyword in pattern["keywords"] 
                                if keyword in message_lower)
            if keyword_matches > 0:
                confidence += 0.3 * (keyword_matches / len(pattern["keywords"]))
            
            # Check for specific indicators
            if "code_indicators" in pattern:
                indicator_matches = sum(1 for indicator in pattern["code_indicators"]
                                     if indicator in message_lower)
                if indicator_matches > 0:
                    confidence += 0.2 * (indicator_matches / len(pattern["code_indicators"]))
            
            if "context_indicators" in pattern:
                context_matches = sum(1 for indicator in pattern["context_indicators"]
                                    if indicator in message_lower)
                if context_matches > 0:
                    confidence += 0.2 * (context_matches / len(pattern["context_indicators"]))
            
            if "scope_indicators" in pattern:
                scope_matches = sum(1 for indicator in pattern["scope_indicators"]
                                  if indicator in message_lower)
                if scope_matches > 0:
                    confidence += 0.2 * (scope_matches / len(pattern["scope_indicators"]))
            
            if "indicators" in pattern:
                general_matches = sum(1 for indicator in pattern["indicators"]
                                    if indicator in message_lower)
                if general_matches > 0:
                    confidence += 0.3 * (general_matches / len(pattern["indicators"]))
            
            # Boost confidence for explicit workflow requests
            if any(phrase in message_lower for phrase in [
                "create workflow", "run workflow", "execute workflow",
                "automate", "pipeline", "process"
            ]):
                confidence += 0.3
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = workflow_type
        
        return {
            "requires_workflow": best_confidence > 0.5,
            "workflow_type": best_match,
            "confidence": best_confidence,
            "analysis": f"Detected {best_match} workflow with {best_confidence:.2f} confidence"
        }
    
    async def _execute_workflow_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """Execute workflow and return formatted response"""
        
        workflow_type = analysis["workflow_type"]
        
        try:
            # Extract parameters from message
            params = await self._extract_workflow_parameters(message, workflow_type)
            
            # Create appropriate workflow
            workflow = await self._create_workflow(workflow_type, params)
            
            if not workflow:
                return f"❌ Failed to create {workflow_type} workflow. Falling back to standard processing."
            
            # Execute workflow
            logger.info(f"Executing {workflow_type} workflow: {workflow.workflow_id}")
            completed_workflow = await self.workflow_engine.execute_workflow(workflow)
            
            # Format response
            return await self._format_workflow_response(completed_workflow, message)
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return f"❌ Workflow execution failed: {str(e)}\\n\\nFalling back to standard processing..."
    
    async def _extract_workflow_parameters(self, message: str, workflow_type: str) -> Dict[str, Any]:
        """Extract parameters for workflow creation from message"""
        
        params = {"original_message": message}
        
        # Use our code review specialist to extract parameters
        if hasattr(self, 'orchestrator') and self.orchestrator:
            try:
                extraction_prompt = f"""
Extract specific parameters from this user message for a {workflow_type} workflow:

Message: "{message}"

Extract and return a JSON object with relevant parameters such as:
- file_path (if specific file mentioned)
- project_path (if project/directory mentioned)
- environment (if deployment target mentioned)
- issue_description (if bug/problem described)
- priority (if urgency mentioned)
- requirements (if specific needs mentioned)

Return only the JSON object, no other text.
"""
                
                result = await self.orchestrator.coordinate_specialists(
                    extraction_prompt,
                    ["code_review"],
                    coordination_strategy="single"
                )
                
                # Try to parse as JSON
                try:
                    extracted_params = json.loads(result)
                    params.update(extracted_params)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse extracted parameters as JSON")
            
            except Exception as e:
                logger.warning(f"Parameter extraction failed: {str(e)}")
        
        return params
    
    async def _create_workflow(self, workflow_type: str, params: Dict[str, Any]) -> Optional[Workflow]:
        """Create appropriate workflow based on type and parameters"""
        
        try:
            if workflow_type == "code_review":
                file_path = params.get("file_path", "code_to_review.py")
                return WorkflowTemplates.code_review_pipeline(file_path)
            
            elif workflow_type == "deployment":
                project_path = params.get("project_path", ".")
                environment = params.get("environment", "production")
                return WorkflowTemplates.deployment_pipeline(project_path, environment)
            
            elif workflow_type == "project_analysis":
                project_path = params.get("project_path", ".")
                return WorkflowTemplates.project_analysis_workflow(project_path)
            
            elif workflow_type == "bug_fix":
                issue_description = params.get("issue_description", params.get("original_message", "Unknown issue"))
                code_files = params.get("code_files", [])
                return WorkflowTemplates.bug_fix_workflow(issue_description, code_files)
            
            else:
                logger.warning(f"Unknown workflow type: {workflow_type}")
                return None
        
        except Exception as e:
            logger.error(f"Workflow creation failed: {str(e)}")
            return None
    
    async def _format_workflow_response(self, workflow: Workflow, original_message: str) -> str:
        """Format workflow execution results into user-friendly response"""
        
        if workflow.status == WorkflowStatus.COMPLETED:
            response = f"✅ **{workflow.name} Complete!**\\n\\n"
            
            # Add execution summary
            execution_time = 0.0
            if workflow.execution_start and workflow.execution_end:
                execution_time = (workflow.execution_end - workflow.execution_start).total_seconds()
            
            response += f"**Execution Summary:**\\n"
            response += f"- Workflow: {workflow.name}\\n"
            response += f"- Tasks Completed: {len([t for t in workflow.tasks if t.status.value == 'completed'])}\\n"
            response += f"- Execution Time: {execution_time:.1f} seconds\\n\\n"
            
            # Add key results
            response += "**Key Results:**\\n\\n"
            
            for task in workflow.tasks:
                if task.status.value == "completed" and task.task_id in workflow.context.results:
                    result = workflow.context.results[task.task_id]
                    if result.output:
                        response += f"### {task.name}\\n"
                        # Truncate long outputs
                        output_str = str(result.output)
                        if len(output_str) > 500:
                            output_str = output_str[:500] + "...\\n\\n[Output truncated - full results available in workflow context]"
                        response += f"{output_str}\\n\\n"
            
            # Add recommendations
            if workflow.context.results:
                response += "**Next Steps:**\\n"
                response += "- Review detailed findings above\\n"
                response += "- Implement recommended improvements\\n"
                response += "- Run validation workflows as needed\\n"
                response += f"- Workflow ID: `{workflow.workflow_id}` for reference\\n"
        
        elif workflow.status == WorkflowStatus.FAILED:
            response = f"❌ **{workflow.name} Failed**\\n\\n"
            
            failed_tasks = [t for t in workflow.tasks if t.status.value == "failed"]
            if failed_tasks:
                response += "**Failed Tasks:**\\n"
                for task in failed_tasks:
                    result = workflow.context.results.get(task.task_id)
                    error = result.error if result else "Unknown error"
                    response += f"- {task.name}: {error}\\n"
            
            response += "\\n**Recommendation:** Try breaking down the request into smaller parts or check the specific error details."
        
        else:
            response = f"⚠️ **{workflow.name} Status: {workflow.status.value}**\\n\\n"
            response += "The workflow did not complete successfully. Please check the workflow status and try again."
        
        return response
    
    async def execute_workflow_by_name(self, 
                                     workflow_name: str, 
                                     parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific workflow by name with parameters"""
        
        if not self.enable_workflows:
            return {"success": False, "error": "Workflows are disabled"}
        
        try:
            # Create workflow based on name
            workflow = None
            
            if workflow_name == "code_review":
                workflow = WorkflowTemplates.code_review_pipeline(
                    parameters.get("file_path", "code.py")
                )
            elif workflow_name == "deployment":
                workflow = WorkflowTemplates.deployment_pipeline(
                    parameters.get("project_path", "."),
                    parameters.get("environment", "production")
                )
            elif workflow_name == "project_analysis":
                workflow = WorkflowTemplates.project_analysis_workflow(
                    parameters.get("project_path", ".")
                )
            elif workflow_name == "bug_fix":
                workflow = WorkflowTemplates.bug_fix_workflow(
                    parameters.get("issue_description", "Bug to fix"),
                    parameters.get("code_files", [])
                )
            else:
                return {"success": False, "error": f"Unknown workflow: {workflow_name}"}
            
            # Execute workflow
            result = await self.workflow_engine.execute_workflow(workflow)
            
            return {
                "success": result.status == WorkflowStatus.COMPLETED,
                "workflow_id": result.workflow_id,
                "status": result.status.value,
                "results": {task_id: result.output for task_id, result in result.context.results.items()}
            }
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running or completed workflow"""
        
        if not self.workflow_engine:
            return None
        
        return self.workflow_engine.get_workflow_status(workflow_id)
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        
        if not self.workflow_engine:
            return []
        
        workflows = []
        for workflow_id, workflow in self.workflow_engine.active_workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "task_count": len(workflow.tasks),
                "completed_tasks": len([t for t in workflow.tasks if t.status.value == "completed"]),
                "start_time": workflow.execution_start
            })
        
        return workflows
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        
        if not self.workflow_engine:
            return False
        
        return self.workflow_engine.cancel_workflow(workflow_id)
    
    def get_available_workflows(self) -> List[Dict[str, str]]:
        """Get list of available workflow templates"""
        
        return [
            {
                "name": "code_review",
                "description": "Comprehensive code review with security, quality, testing, and architecture analysis"
            },
            {
                "name": "deployment",
                "description": "Complete deployment pipeline with validation, testing, and monitoring setup"
            },
            {
                "name": "project_analysis", 
                "description": "Comprehensive project analysis across all technical dimensions"
            },
            {
                "name": "bug_fix",
                "description": "Automated bug fix workflow with analysis, solution design, and validation"
            }
        ]
    
    async def system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including workflows"""
        
        # Get base status from parent
        status = await super().system_status()
        
        # Add workflow information
        if self.enable_workflows:
            workflow_status = {
                "workflows_enabled": True,
                "active_workflows": len(self.workflow_engine.active_workflows),
                "completed_workflows": len(self.workflow_engine.completed_workflows),
                "workflow_history_count": len(self.workflow_engine.workflow_history),
                "available_integrations": self.integration_manager.get_available_adapters() if self.integration_manager else []
            }
        else:
            workflow_status = {"workflows_enabled": False}
        
        status["workflow_system"] = workflow_status
        return status

# Convenience function for creating workflow-enabled Jarvis
def create_workflow_jarvis(enable_mcp: bool = True,
                         enable_multi_agent: bool = True,
                         enable_workflows: bool = True) -> WorkflowJarvisAgent:
    """Create a workflow-enabled Jarvis agent"""
    
    return WorkflowJarvisAgent(
        enable_mcp=enable_mcp,
        enable_multi_agent=enable_multi_agent,
        enable_workflows=enable_workflows
    )
