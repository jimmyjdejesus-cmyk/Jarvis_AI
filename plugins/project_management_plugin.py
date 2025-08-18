"""
Example plugin demonstrating advanced features of the Jarvis AI plugin architecture.

This plugin shows:
1. Custom automation workflows
2. External API integration
3. Approval workflows
4. Output chaining between steps
"""

import os
import json
import time
from typing import Dict, Any, Optional

from agent.plugin_base import (
    AutomationPlugin, PluginMetadata, PluginAction, PluginResult, PluginType
)


class ProjectManagementPlugin(AutomationPlugin):
    """Plugin for managing development projects with workflow automation."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ProjectManagementPlugin",
            description="Automate project management tasks like creating issues, managing releases, and deploying",
            version="1.0.0",
            author="Jarvis AI Team",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "create project", "setup project", "create issue", "deploy project",
                "release version", "project status", "project setup"
            ],
            tags=["project", "automation", "deployment", "issues"],
            dependencies=["requests"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        """Check if this plugin can handle the command."""
        project_keywords = ["project", "issue", "deploy", "release", "setup"]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in project_keywords)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        """Parse natural language command into action."""
        if not self.can_handle(command, context):
            return None
        
        command_lower = command.lower()
        
        # Project setup workflow
        if "setup project" in command_lower or "create project" in command_lower:
            return self._parse_project_setup(command, context)
        
        # Issue creation
        elif "create issue" in command_lower:
            return self._parse_issue_creation(command, context)
        
        # Deployment
        elif "deploy" in command_lower:
            return self._parse_deployment(command, context)
        
        # Release management
        elif "release" in command_lower:
            return self._parse_release(command, context)
        
        # Project status
        elif "project status" in command_lower:
            return self._parse_project_status(command, context)
        
        return None
    
    def _parse_project_setup(self, command: str, context: Dict[str, Any] = None) -> PluginAction:
        """Parse project setup commands."""
        # Extract project name from command
        parts = command.lower().split("project")
        project_name = "new-project"
        
        if len(parts) > 1:
            name_part = parts[1].strip()
            if name_part.startswith("named") or name_part.startswith("called"):
                project_name = name_part.split(None, 1)[1] if len(name_part.split()) > 1 else "new-project"
            elif name_part:
                project_name = name_part.split()[0]
        
        return PluginAction(
            name="project_setup",
            description=f"Setup new project '{project_name}'",
            args={
                "project_name": project_name,
                "include_git": True,
                "include_readme": True,
                "include_gitignore": True,
                "create_directories": ["src", "tests", "docs"]
            },
            preview=f"Will create project structure for '{project_name}' with git, README, and basic directories",
            requires_approval=False
        )
    
    def _parse_issue_creation(self, command: str, context: Dict[str, Any] = None) -> PluginAction:
        """Parse issue creation commands."""
        # Extract issue title from command
        parts = command.lower().split("issue")
        issue_title = "New Issue"
        
        if len(parts) > 1:
            title_part = parts[1].strip()
            if title_part.startswith("for") or title_part.startswith("about"):
                issue_title = title_part.split(None, 1)[1] if len(title_part.split()) > 1 else "New Issue"
            elif title_part:
                issue_title = title_part
        
        return PluginAction(
            name="create_issue", 
            description=f"Create issue: {issue_title}",
            args={
                "title": issue_title,
                "body": f"Issue created via Jarvis AI: {command}",
                "labels": ["auto-created"],
                "priority": "medium"
            },
            preview=f"Will create GitHub issue: '{issue_title}'",
            requires_approval=True  # Creating issues requires approval
        )
    
    def _parse_deployment(self, command: str, context: Dict[str, Any] = None) -> PluginAction:
        """Parse deployment commands."""
        # Determine deployment target
        target = "staging"
        if "production" in command.lower() or "prod" in command.lower():
            target = "production"
        elif "dev" in command.lower() or "development" in command.lower():
            target = "development"
        
        return PluginAction(
            name="deploy_project",
            description=f"Deploy to {target}",
            args={
                "target": target,
                "run_tests": True,
                "backup_before": target == "production",
                "notify_team": target == "production"
            },
            preview=f"Will deploy project to {target} environment",
            requires_approval=target == "production"  # Production deployments need approval
        )
    
    def _parse_release(self, command: str, context: Dict[str, Any] = None) -> PluginAction:
        """Parse release management commands."""
        # Extract version from command
        version = "1.0.0"
        if "version" in command.lower():
            parts = command.split("version")
            if len(parts) > 1:
                version_part = parts[1].strip().split()[0]
                if version_part:
                    version = version_part
        
        return PluginAction(
            name="create_release",
            description=f"Create release version {version}",
            args={
                "version": version,
                "generate_changelog": True,
                "tag_commit": True,
                "publish_release": True
            },
            preview=f"Will create and publish release version {version}",
            requires_approval=True
        )
    
    def _parse_project_status(self, command: str, context: Dict[str, Any] = None) -> PluginAction:
        """Parse project status commands."""
        return PluginAction(
            name="project_status",
            description="Get project status report",
            args={
                "include_git_status": True,
                "include_issues": True,
                "include_tests": True,
                "include_dependencies": True
            },
            preview="Will generate comprehensive project status report",
            requires_approval=False
        )
    
    def preview_action(self, action: PluginAction) -> str:
        """Generate human-readable preview."""
        action_name = action.name
        args = action.args
        
        if action_name == "project_setup":
            project_name = args.get("project_name", "project")
            dirs = ", ".join(args.get("create_directories", []))
            return f"Setup project '{project_name}' with directories: {dirs}"
        
        elif action_name == "create_issue":
            title = args.get("title", "New Issue")
            return f"Create GitHub issue: '{title}'"
        
        elif action_name == "deploy_project":
            target = args.get("target", "staging")
            extras = []
            if args.get("run_tests"): extras.append("run tests")
            if args.get("backup_before"): extras.append("create backup")
            if args.get("notify_team"): extras.append("notify team")
            extra_text = f" ({', '.join(extras)})" if extras else ""
            return f"Deploy to {target}{extra_text}"
        
        elif action_name == "create_release":
            version = args.get("version", "1.0.0")
            return f"Create release version {version} with changelog and git tag"
        
        elif action_name == "project_status":
            return "Generate project status report (git, issues, tests, dependencies)"
        
        return action.description
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        """Execute the plugin action."""
        try:
            action_name = action.name
            
            if action_name == "project_setup":
                return self._execute_project_setup(action.args)
            elif action_name == "create_issue":
                return self._execute_create_issue(action.args)
            elif action_name == "deploy_project":
                return self._execute_deploy(action.args)
            elif action_name == "create_release":
                return self._execute_create_release(action.args)
            elif action_name == "project_status":
                return self._execute_project_status(action.args)
            else:
                return PluginResult(success=False, output=None, error=f"Unknown action: {action_name}")
        
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def _execute_project_setup(self, args: Dict[str, Any]) -> PluginResult:
        """Execute project setup."""
        project_name = args.get("project_name", "new-project")
        create_dirs = args.get("create_directories", [])
        
        try:
            # Create project directory
            if not os.path.exists(project_name):
                os.makedirs(project_name)
            
            # Create subdirectories
            for dir_name in create_dirs:
                dir_path = os.path.join(project_name, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
            
            # Create README if requested
            if args.get("include_readme", False):
                readme_path = os.path.join(project_name, "README.md")
                with open(readme_path, 'w') as f:
                    f.write(f"# {project_name}\n\nProject created by Jarvis AI\n")
            
            # Create .gitignore if requested
            if args.get("include_gitignore", False):
                gitignore_path = os.path.join(project_name, ".gitignore")
                with open(gitignore_path, 'w') as f:
                    f.write("__pycache__/\n*.pyc\n.env\nnode_modules/\n")
            
            result = {
                "project_name": project_name,
                "directories_created": create_dirs,
                "files_created": []
            }
            
            if args.get("include_readme"): result["files_created"].append("README.md")
            if args.get("include_gitignore"): result["files_created"].append(".gitignore")
            
            return PluginResult(
                success=True,
                output=f"Project '{project_name}' setup complete",
                metadata=result
            )
        
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def _execute_create_issue(self, args: Dict[str, Any]) -> PluginResult:
        """Execute issue creation (simulated)."""
        title = args.get("title", "New Issue")
        body = args.get("body", "")
        labels = args.get("labels", [])
        
        # In a real implementation, this would call GitHub API
        # For demo purposes, we'll simulate the result
        issue_data = {
            "id": 12345,
            "number": 42,
            "title": title,
            "body": body,
            "labels": labels,
            "state": "open",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return PluginResult(
            success=True,
            output=f"Created issue #{issue_data['number']}: {title}",
            metadata=issue_data
        )
    
    def _execute_deploy(self, args: Dict[str, Any]) -> PluginResult:
        """Execute deployment (simulated)."""
        target = args.get("target", "staging")
        
        steps = []
        if args.get("run_tests"):
            steps.append("✅ Tests passed")
        if args.get("backup_before"):
            steps.append("✅ Backup created")
        
        steps.append(f"✅ Deployed to {target}")
        
        if args.get("notify_team"):
            steps.append("✅ Team notified")
        
        return PluginResult(
            success=True,
            output=f"Deployment to {target} successful",
            metadata={
                "target": target,
                "steps": steps,
                "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        )
    
    def _execute_create_release(self, args: Dict[str, Any]) -> PluginResult:
        """Execute release creation (simulated)."""
        version = args.get("version", "1.0.0")
        
        release_data = {
            "version": version,
            "tag": f"v{version}",
            "changelog_generated": args.get("generate_changelog", False),
            "commit_tagged": args.get("tag_commit", False),
            "published": args.get("publish_release", False),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return PluginResult(
            success=True,
            output=f"Release {version} created and published",
            metadata=release_data
        )
    
    def _execute_project_status(self, args: Dict[str, Any]) -> PluginResult:
        """Execute project status check."""
        status_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "git_status": "clean" if args.get("include_git_status") else "not checked",
            "open_issues": 3 if args.get("include_issues") else "not checked", 
            "test_status": "passing" if args.get("include_tests") else "not checked",
            "dependencies": "up to date" if args.get("include_dependencies") else "not checked"
        }
        
        report_text = f"""Project Status Report - {status_report['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Git Status: {status_report['git_status']}
🐛 Open Issues: {status_report['open_issues']}
🧪 Tests: {status_report['test_status']}
📦 Dependencies: {status_report['dependencies']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return PluginResult(
            success=True,
            output=report_text,
            metadata=status_report
        )
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema for workflow chaining."""
        return {
            "project_name": str,
            "status": str,
            "metadata": dict,
            "files_created": list,
            "version": str
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema for workflow chaining."""
        return {
            "project_name": str,
            "target": str,
            "version": str,
            "title": str
        }