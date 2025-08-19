"""
Plugin adapters for existing Jarvis AI tools.

This module provides plugin wrappers for existing tools to make them
compatible with the new plugin architecture while maintaining backward compatibility.
"""

import os
from typing import Dict, List, Any, Optional

from agent.plugin_base import (
    AutomationPlugin, IntegrationPlugin, CommandPlugin,
    PluginMetadata, PluginAction, PluginResult, PluginType
)

# Import existing tool modules
try:
    import agent.github_integration as github_integration
    import agent.jetbrains_integration as jetbrains_integration
    import agent.note_integration as note_integration
    import agent.code_review as code_review
    import agent.code_search as code_search
    import agent.repo_context as repo_context
    import agent.browser_automation as browser_automation
except ImportError as e:
    print(f"Warning: Could not import some agent modules: {e}")


class GitPlugin(AutomationPlugin):
    """Plugin wrapper for git operations."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="GitPlugin",
            description="Execute git commands and repository operations",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "git status", "git commit", "git diff", "git push", "git pull", 
                "git checkout", "git branch", "git log", "repository status"
            ],
            tags=["git", "repository", "version-control"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        command_lower = command.lower()
        git_commands = ["git", "repo", "repository", "commit", "branch", "push", "pull", "checkout"]
        return any(cmd in command_lower for cmd in git_commands)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        if not self.can_handle(command, context):
            return None
        
        return PluginAction(
            name="git_command",
            description=f"Execute git command: {command}",
            args={
                "command": command,
                "repository_path": context.get("repository_path") if context else None
            },
            preview=f"Will execute git command: {command}",
            requires_approval=any(word in command.lower() for word in ["push", "commit", "merge", "delete"])
        )
    
    def preview_action(self, action: PluginAction) -> str:
        command = action.args.get("command", "")
        repo_path = action.args.get("repository_path", "current directory")
        return f"Execute git command '{command}' in {repo_path}"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            command = action.args.get("command", "")
            repository_path = action.args.get("repository_path")
            
            if hasattr(github_integration, 'execute_git_command'):
                result = github_integration.execute_git_command(command, repository_path)
                return PluginResult(success=True, output=result)
            else:
                return PluginResult(success=False, output=None, error="Git integration not available")
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "output": str,
            "status": str,
            "files_changed": list
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "command": str,
            "repository_path": str
        }


class IDEPlugin(AutomationPlugin):
    """Plugin wrapper for IDE operations."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="IDEPlugin", 
            description="Open files and projects in JetBrains IDEs",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "open in pycharm", "open in intellij", "open in idea", 
                "open in webstorm", "open in phpstorm", "launch ide"
            ],
            tags=["ide", "jetbrains", "editor"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        command_lower = command.lower()
        ide_commands = ["open in", "pycharm", "intellij", "idea", "webstorm", "phpstorm", "launch"]
        return any(cmd in command_lower for cmd in ide_commands)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        if not self.can_handle(command, context):
            return None
        
        return PluginAction(
            name="ide_command",
            description=f"Execute IDE command: {command}",
            args={"command": command},
            preview=f"Will execute IDE command: {command}",
            requires_approval=False
        )
    
    def preview_action(self, action: PluginAction) -> str:
        command = action.args.get("command", "")
        return f"Execute IDE command: {command}"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            command = action.args.get("command", "")
            
            if hasattr(jetbrains_integration, 'execute_ide_command'):
                result = jetbrains_integration.execute_ide_command(command)
                return PluginResult(success=True, output=result)
            else:
                return PluginResult(success=False, output=None, error="IDE integration not available")
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {"output": str, "success": bool}
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {"command": str}


class CodeReviewPlugin(AutomationPlugin):
    """Plugin wrapper for code review functionality."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="CodeReviewPlugin",
            description="Analyze code quality, style, and security",
            version="1.0.0", 
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "review code", "code review", "analyze code", "check code quality",
                "code analysis", "security review"
            ],
            tags=["code-review", "quality", "security", "analysis"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        command_lower = command.lower()
        review_commands = ["review", "analyze", "check", "quality", "security", "style"]
        code_commands = ["code", "file", "function", "class"]
        return any(r in command_lower for r in review_commands) and any(c in command_lower for c in code_commands)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        if not self.can_handle(command, context):
            return None
        
        # Try to extract file path from command or context
        file_path = ""
        if context and "files" in context:
            file_path = context["files"][0] if context["files"] else ""
        
        # Extract check types
        check_types = []
        if "style" in command.lower():
            check_types.append("style")
        if "security" in command.lower():
            check_types.append("security")
        if "quality" in command.lower():
            check_types.append("quality")
        if not check_types:
            check_types = ["all"]
        
        return PluginAction(
            name="code_review",
            description=f"Review code: {command}",
            args={
                "file_path": file_path,
                "check_types": check_types
            },
            preview=f"Will review code for {', '.join(check_types)} issues",
            requires_approval=False
        )
    
    def preview_action(self, action: PluginAction) -> str:
        file_path = action.args.get("file_path", "specified files")
        check_types = action.args.get("check_types", ["all"])
        return f"Review {file_path} for {', '.join(check_types)} issues"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            file_path = action.args.get("file_path", "")
            check_types = action.args.get("check_types", ["all"])
            
            if hasattr(code_review, 'review_file'):
                result = code_review.review_file(file_path, check_types)
                return PluginResult(success=True, output=result)
            else:
                return PluginResult(success=False, output=None, error="Code review not available")
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "issues": list,
            "score": float,
            "recommendations": list
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "file_path": str,
            "check_types": list
        }


class CodeSearchPlugin(AutomationPlugin):
    """Plugin wrapper for code search functionality."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="CodeSearchPlugin",
            description="Search for code, functions, classes, and variables",
            version="1.0.0",
            author="Jarvis AI", 
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "search code", "find function", "find class", "search for",
                "locate code", "code search"
            ],
            tags=["search", "code", "functions", "classes"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        command_lower = command.lower()
        search_commands = ["search", "find", "locate", "look for"]
        code_commands = ["code", "function", "class", "variable", "method"]
        return any(s in command_lower for s in search_commands) and any(c in command_lower for c in code_commands)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        if not self.can_handle(command, context):
            return None
        
        # Extract search query
        query = command
        for prefix in ["search for", "find", "locate", "search code for"]:
            if prefix in command.lower():
                query = command.lower().split(prefix, 1)[1].strip()
                break
        
        return PluginAction(
            name="code_search",
            description=f"Search code: {command}",
            args={
                "query": query,
                "search_type": "all",
                "repository_path": context.get("repository_path") if context else None,
                "case_sensitive": False,
                "regex": False
            },
            preview=f"Will search for '{query}' in code",
            requires_approval=False
        )
    
    def preview_action(self, action: PluginAction) -> str:
        query = action.args.get("query", "")
        repo_path = action.args.get("repository_path", "current repository")
        return f"Search for '{query}' in {repo_path}"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            query = action.args.get("query", "")
            search_type = action.args.get("search_type", "all")
            repository_path = action.args.get("repository_path")
            case_sensitive = action.args.get("case_sensitive", False)
            regex = action.args.get("regex", False)
            
            if hasattr(code_search, 'search_code'):
                result = code_search.search_code(query, repository_path, search_type, case_sensitive, regex)
                return PluginResult(success=True, output=result)
            else:
                return PluginResult(success=False, output=None, error="Code search not available")
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "matches": list,
            "files": list,
            "locations": list
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "query": str,
            "search_type": str,
            "repository_path": str
        }


class BrowserAutomationPlugin(AutomationPlugin):
    """Plugin wrapper for browser automation."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="BrowserAutomationPlugin",
            description="Automate web browser tasks",
            version="1.0.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "go to", "browse", "open website", "search google", "automate browser"
            ],
            tags=["browser", "web", "automation"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        command_lower = command.lower()
        browser_commands = ["go to", "browse", "open", "website", "search google", "browser"]
        return any(cmd in command_lower for cmd in browser_commands)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        if not self.can_handle(command, context):
            return None
        
        return PluginAction(
            name="browser_automation",
            description=f"Browser automation: {command}",
            args={"actions": command},
            preview=f"Will automate browser: {command}",
            requires_approval=True  # Browser automation can be sensitive
        )
    
    def preview_action(self, action: PluginAction) -> str:
        actions = action.args.get("actions", "")
        return f"Automate browser: {actions}"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            actions = action.args.get("actions", [])
            
            if hasattr(browser_automation, 'automate_browser'):
                result = browser_automation.automate_browser(actions)
                return PluginResult(success=True, output=result)
            else:
                return PluginResult(success=False, output=None, error="Browser automation not available")
        except Exception as e:
            return PluginResult(success=False, output=None, error=str(e))
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {"results": list, "success": bool}
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {"actions": [str, list]}