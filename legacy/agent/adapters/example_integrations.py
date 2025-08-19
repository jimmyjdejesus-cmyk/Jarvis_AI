#!/usr/bin/env python3
"""
Example Plugin Integrations for Common Tools

This module demonstrates how to create plugins for common development tools
using the Jarvis AI Extensibility SDK.
"""

import os
import subprocess
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from agent.adapters.extensibility_sdk import (
    PluginSDK, BuildSystemPlugin, TestingFrameworkPlugin, 
    LanguageEnhancerPlugin, jarvis_tool, build_system, testing_framework
)
from agent.adapters.plugin_base import (
    AutomationPlugin, PluginMetadata, PluginAction, PluginResult, PluginType
)


class GitPlugin(AutomationPlugin):
    """Enhanced Git integration plugin with common operations."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Git Integration",
            description="Comprehensive git operations including status, commit, push, branch management",
            version="1.2.0",
            author="Jarvis AI",
            plugin_type=PluginType.AUTOMATION,
            triggers=[
                "git status", "git commit", "git push", "git pull", "git branch",
                "git checkout", "git diff", "git log", "check git status",
                "commit changes", "push to remote", "create branch"
            ],
            tags=["git", "vcs", "version-control", "repository"]
        )
    
    def can_handle(self, command: str, context: Dict[str, Any] = None) -> bool:
        git_keywords = ["git", "commit", "push", "pull", "branch", "checkout", "repository", "repo"]
        return any(keyword in command.lower() for keyword in git_keywords)
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[PluginAction]:
        command_lower = command.lower()
        
        if "status" in command_lower:
            return PluginAction(
                name="git_status",
                description="Check git repository status",
                args={"path": context.get("repository_path", ".") if context else "."}
            )
        elif "commit" in command_lower:
            # Extract commit message if provided
            message = "Auto-commit via Jarvis AI"
            if '"' in command:
                parts = command.split('"')
                if len(parts) >= 2:
                    message = parts[1]
            
            return PluginAction(
                name="git_commit",
                description=f"Commit changes with message: {message}",
                args={"message": message, "path": context.get("repository_path", ".") if context else "."},
                requires_approval=True
            )
        elif "push" in command_lower:
            return PluginAction(
                name="git_push",
                description="Push changes to remote repository",
                args={"path": context.get("repository_path", ".") if context else "."},
                requires_approval=True
            )
        elif "pull" in command_lower:
            return PluginAction(
                name="git_pull",
                description="Pull changes from remote repository",
                args={"path": context.get("repository_path", ".") if context else "."},
                requires_approval=True
            )
        elif "branch" in command_lower:
            return PluginAction(
                name="git_branch",
                description="List or manage git branches",
                args={"path": context.get("repository_path", ".") if context else "."}
            )
        
        return None
    
    def preview_action(self, action: PluginAction) -> str:
        """Preview what the git action will do."""
        if action.name == "git_status":
            return "Check git repository status (shows modified files)"
        elif action.name == "git_commit":
            message = action.args.get("message", "Auto-commit")
            return f"Add all files and commit with message: '{message}'"
        elif action.name == "git_push":
            return "Push local commits to remote repository"
        elif action.name == "git_pull":
            return "Pull latest changes from remote repository"
        elif action.name == "git_branch":
            return "List all local and remote branches"
        else:
            return f"Execute git action: {action.description}"
    
    def execute_action(self, action: PluginAction, context: Dict[str, Any] = None) -> PluginResult:
        try:
            path = action.args.get("path", ".")
            
            if action.name == "git_status":
                result = subprocess.run(
                    ["git", "status", "--porcelain"], 
                    cwd=path, capture_output=True, text=True
                )
                if result.returncode == 0:
                    return PluginResult(
                        success=True,
                        output=f"Git status:\n{result.stdout}" if result.stdout else "Working tree clean"
                    )
                else:
                    return PluginResult(success=False, error=result.stderr)
            
            elif action.name == "git_commit":
                message = action.args.get("message", "Auto-commit")
                
                # Add all changes first
                add_result = subprocess.run(
                    ["git", "add", "."], 
                    cwd=path, capture_output=True, text=True
                )
                
                if add_result.returncode != 0:
                    return PluginResult(success=False, error=f"Git add failed: {add_result.stderr}")
                
                # Commit changes
                commit_result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=path, capture_output=True, text=True
                )
                
                if commit_result.returncode == 0:
                    return PluginResult(success=True, output=f"Committed with message: {message}")
                else:
                    return PluginResult(success=False, error=commit_result.stderr)
            
            elif action.name == "git_push":
                result = subprocess.run(
                    ["git", "push"],
                    cwd=path, capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(success=True, output="Successfully pushed to remote")
                else:
                    return PluginResult(success=False, error=result.stderr)
            
            elif action.name == "git_pull":
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=path, capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(success=True, output="Successfully pulled from remote")
                else:
                    return PluginResult(success=False, error=result.stderr)
            
            elif action.name == "git_branch":
                result = subprocess.run(
                    ["git", "branch", "-a"],
                    cwd=path, capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(success=True, output=f"Git branches:\n{result.stdout}")
                else:
                    return PluginResult(success=False, error=result.stderr)
            
            return PluginResult(success=False, error=f"Unknown action: {action.name}")
            
        except Exception as e:
            return PluginResult(success=False, error=str(e))


class NpmBuildSystemPlugin(BuildSystemPlugin):
    """NPM/Node.js build system integration."""
    
    def get_build_system_name(self) -> str:
        return "npm"
    
    def detect_build_system(self, project_path: str) -> bool:
        package_json = Path(project_path) / "package.json"
        return package_json.exists()
    
    def get_build_commands(self, project_path: str) -> List[Dict[str, Any]]:
        commands = []
        package_json_path = Path(project_path) / "package.json"
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                scripts = package_data.get("scripts", {})
                for script_name, script_command in scripts.items():
                    commands.append({
                        "name": script_name,
                        "command": f"npm run {script_name}",
                        "description": f"Run npm script: {script_name}",
                        "script": script_command
                    })
            except Exception:
                pass
        
        # Add standard npm commands
        standard_commands = [
            {"name": "install", "command": "npm install", "description": "Install dependencies"},
            {"name": "update", "command": "npm update", "description": "Update dependencies"},
            {"name": "audit", "command": "npm audit", "description": "Check for security vulnerabilities"},
            {"name": "clean", "command": "npm cache clean --force", "description": "Clean npm cache"}
        ]
        
        commands.extend(standard_commands)
        return commands
    
    def execute_build_command(self, command: str, project_path: str,
                            options: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command.split(),
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "return_code": -1
            }


class PipBuildSystemPlugin(BuildSystemPlugin):
    """Python pip build system integration."""
    
    def get_build_system_name(self) -> str:
        return "pip"
    
    def detect_build_system(self, project_path: str) -> bool:
        requirements_files = [
            "requirements.txt", "requirements-dev.txt", "setup.py", 
            "pyproject.toml", "environment.yml", "Pipfile"
        ]
        project_pathlib = Path(project_path)
        return any((project_pathlib / req_file).exists() for req_file in requirements_files)
    
    def get_build_commands(self, project_path: str) -> List[Dict[str, Any]]:
        commands = []
        project_pathlib = Path(project_path)
        
        # Detect which files are present and add appropriate commands
        if (project_pathlib / "requirements.txt").exists():
            commands.append({
                "name": "install-requirements",
                "command": "pip install -r requirements.txt",
                "description": "Install dependencies from requirements.txt"
            })
        
        if (project_pathlib / "setup.py").exists():
            commands.extend([
                {"name": "install-dev", "command": "pip install -e .", "description": "Install in development mode"},
                {"name": "build", "command": "python setup.py build", "description": "Build package"},
                {"name": "sdist", "command": "python setup.py sdist", "description": "Create source distribution"}
            ])
        
        if (project_pathlib / "pyproject.toml").exists():
            commands.extend([
                {"name": "build-modern", "command": "python -m build", "description": "Build using pyproject.toml"},
                {"name": "install-build", "command": "pip install build", "description": "Install build tools"}
            ])
        
        # Standard pip commands
        standard_commands = [
            {"name": "list", "command": "pip list", "description": "List installed packages"},
            {"name": "freeze", "command": "pip freeze", "description": "Output installed packages in requirements format"},
            {"name": "check", "command": "pip check", "description": "Verify installed packages have compatible dependencies"}
        ]
        
        commands.extend(standard_commands)
        return commands
    
    def execute_build_command(self, command: str, project_path: str,
                            options: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command.split(),
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600  # Longer timeout for pip operations
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 10 minutes",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "return_code": -1
            }


class PytestTestingPlugin(TestingFrameworkPlugin):
    """Pytest testing framework integration."""
    
    def get_framework_name(self) -> str:
        return "pytest"
    
    def detect_framework(self, project_path: str) -> bool:
        project_pathlib = Path(project_path)
        
        # Check for pytest configuration files
        pytest_configs = ["pytest.ini", "pyproject.toml", "setup.cfg"]
        if any((project_pathlib / config).exists() for config in pytest_configs):
            return True
        
        # Check for test files with pytest naming convention
        test_patterns = ["test_*.py", "*_test.py", "tests/*.py"]
        for pattern in test_patterns:
            if list(project_pathlib.glob(pattern)) or list(project_pathlib.glob(f"**/{pattern}")):
                return True
        
        return False
    
    def get_test_commands(self, project_path: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": "run-all", 
                "command": "pytest",
                "description": "Run all tests"
            },
            {
                "name": "run-verbose",
                "command": "pytest -v",
                "description": "Run all tests with verbose output"
            },
            {
                "name": "run-coverage",
                "command": "pytest --cov=.",
                "description": "Run tests with coverage report"
            },
            {
                "name": "run-markers",
                "command": "pytest -m 'not slow'",
                "description": "Run tests excluding slow markers"
            },
            {
                "name": "run-failed",
                "command": "pytest --lf",
                "description": "Run only previously failed tests"
            },
            {
                "name": "collect-only",
                "command": "pytest --collect-only",
                "description": "Collect tests without running them"
            }
        ]
    
    def run_tests(self, test_path: str = None, project_path: str = None,
                 options: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            cmd = ["pytest"]
            
            if test_path:
                cmd.append(test_path)
            
            if options:
                if options.get("verbose", False):
                    cmd.append("-v")
                if options.get("coverage", False):
                    cmd.extend(["--cov=."])
                if options.get("failed_only", False):
                    cmd.append("--lf")
                if "markers" in options:
                    cmd.extend(["-m", options["markers"]])
            
            result = subprocess.run(
                cmd,
                cwd=project_path or ".",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "tests_passed": "failed" not in result.stdout.lower() and result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tests timed out after 5 minutes",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "return_code": -1
            }


class JestTestingPlugin(TestingFrameworkPlugin):
    """Jest testing framework integration for JavaScript/TypeScript."""
    
    def get_framework_name(self) -> str:
        return "jest"
    
    def detect_framework(self, project_path: str) -> bool:
        project_pathlib = Path(project_path)
        
        # Check for Jest configuration
        jest_configs = ["jest.config.js", "jest.config.json", "package.json"]
        
        if (project_pathlib / "package.json").exists():
            try:
                with open(project_pathlib / "package.json", 'r') as f:
                    package_data = json.load(f)
                    if "jest" in package_data.get("devDependencies", {}) or \
                       "jest" in package_data.get("dependencies", {}) or \
                       "jest" in package_data.get("scripts", {}):
                        return True
            except Exception:
                pass
        
        # Check for test files
        test_patterns = ["*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts"]
        for pattern in test_patterns:
            if list(project_pathlib.glob(f"**/{pattern}")):
                return True
        
        return False
    
    def get_test_commands(self, project_path: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": "run-all",
                "command": "npm test",
                "description": "Run all Jest tests"
            },
            {
                "name": "run-watch",
                "command": "npm test -- --watch",
                "description": "Run tests in watch mode"
            },
            {
                "name": "run-coverage",
                "command": "npm test -- --coverage",
                "description": "Run tests with coverage report"
            },
            {
                "name": "run-update-snapshots",
                "command": "npm test -- --updateSnapshot",
                "description": "Update test snapshots"
            },
            {
                "name": "run-verbose",
                "command": "npm test -- --verbose",
                "description": "Run tests with verbose output"
            }
        ]
    
    def run_tests(self, test_path: str = None, project_path: str = None,
                 options: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            cmd = ["npm", "test"]
            
            jest_args = []
            if test_path:
                jest_args.append(test_path)
            
            if options:
                if options.get("watch", False):
                    jest_args.append("--watch")
                if options.get("coverage", False):
                    jest_args.append("--coverage")
                if options.get("verbose", False):
                    jest_args.append("--verbose")
                if options.get("update_snapshots", False):
                    jest_args.append("--updateSnapshot")
            
            if jest_args:
                cmd.extend(["--"] + jest_args)
            
            result = subprocess.run(
                cmd,
                cwd=project_path or ".",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "tests_passed": "Tests:" in result.stdout and "failed" not in result.stdout.lower()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tests timed out after 5 minutes",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "return_code": -1
            }


# Plugin registration function
def register_example_plugins():
    """Register all example plugins with the plugin manager."""
    plugins = [
        GitPlugin(),
        NpmBuildSystemPlugin(),
        PipBuildSystemPlugin(), 
        PytestTestingPlugin(),
        JestTestingPlugin()
    ]
    
    registered_count = 0
    for plugin in plugins:
        if PluginSDK.register_plugin(plugin):
            registered_count += 1
    
    return registered_count


# Decorated functions using the @jarvis_tool decorator
@jarvis_tool(
    name="git_quick_status",
    description="Quick git status check with enhanced formatting",
    triggers=["quick git status", "git summary"]
)
def git_quick_status(repository_path: str = ".") -> str:
    """Get a quick overview of git repository status."""
    try:
        # Get basic status
        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--branch"],
            cwd=repository_path,
            capture_output=True,
            text=True
        )
        
        if status_result.returncode != 0:
            return f"Error: {status_result.stderr}"
        
        lines = status_result.stdout.strip().split('\n')
        if not lines or not lines[0]:
            return "Repository is clean, no changes detected."
        
        branch_line = lines[0] if lines[0].startswith('##') else "## Unknown branch"
        file_lines = [line for line in lines[1:] if line.strip()]
        
        summary = [f"Branch: {branch_line[3:]}"]
        
        if file_lines:
            summary.append(f"Changes: {len(file_lines)} files modified")
            summary.extend([f"  {line}" for line in file_lines[:5]])  # Show first 5 files
            if len(file_lines) > 5:
                summary.append(f"  ... and {len(file_lines) - 5} more files")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"Error checking git status: {str(e)}"


@jarvis_tool(
    name="project_test_runner",
    description="Automatically detect and run tests for a project",
    triggers=["run tests", "test project", "execute tests"]
)
def project_test_runner(project_path: str = ".", test_type: str = "auto") -> str:
    """Automatically detect and run appropriate tests for a project."""
    try:
        project_pathlib = Path(project_path)
        
        # Detect testing framework
        if test_type == "auto":
            if JestTestingPlugin().detect_framework(project_path):
                framework = JestTestingPlugin()
            elif PytestTestingPlugin().detect_framework(project_path):
                framework = PytestTestingPlugin()
            else:
                return "No supported testing framework detected in this project."
        elif test_type == "jest":
            framework = JestTestingPlugin()
        elif test_type == "pytest":
            framework = PytestTestingPlugin()
        else:
            return f"Unsupported test type: {test_type}"
        
        # Run tests
        result = framework.run_tests(project_path=project_path)
        
        if result["success"]:
            return f"✅ Tests passed!\n\nOutput:\n{result['output']}"
        else:
            return f"❌ Tests failed!\n\nError:\n{result['error']}\n\nOutput:\n{result['output']}"
            
    except Exception as e:
        return f"Error running tests: {str(e)}"


if __name__ == "__main__":
    # Example usage and testing
    print("Registering example plugins...")
    count = register_example_plugins()
    print(f"Registered {count} plugins successfully!")
    
    # Test the decorated functions
    print("\nTesting git_quick_status:")
    print(git_quick_status())
    
    print("\nTesting project_test_runner:")
    print(project_test_runner())