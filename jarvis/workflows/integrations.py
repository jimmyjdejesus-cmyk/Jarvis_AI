"""
🚀 PHASE 4: INTEGRATION ADAPTERS

Deep system integration capabilities for workflow execution including
file operations, code generation, testing automation, and external tool integration.
"""

import os
import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from abc import ABC, abstractmethod
import tempfile
import shutil
import logging
import ast

logger = logging.getLogger(__name__)

# Lazy-import placeholders for optional Jarvis modules
get_coding_agent = None  # type: ignore
jarvis_agent = None  # type: ignore

class IntegrationAdapter(ABC):
    """Base class for system integration adapters"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration action with parameters"""
        pass
    
    def is_available(self) -> bool:
        """Check if integration is available"""
        return self.enabled

class FileSystemAdapter(IntegrationAdapter):
    """File system operations for workflows"""
    
    def __init__(self):
        super().__init__("filesystem")
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system operations"""
        
        try:
            if action == "read_file":
                return await self._read_file(params)
            elif action == "write_file":
                return await self._write_file(params)
            elif action == "list_directory":
                return await self._list_directory(params)
            elif action == "create_directory":
                return await self._create_directory(params)
            elif action == "delete_file":
                return await self._delete_file(params)
            elif action == "copy_file":
                return await self._copy_file(params)
            elif action == "move_file":
                return await self._move_file(params)
            elif action == "find_files":
                return await self._find_files(params)
            elif action == "get_file_info":
                return await self._get_file_info(params)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"FileSystem adapter error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        file_path = params.get("path")
        encoding = params.get("encoding", "utf-8")
        
        if not file_path or not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        file_path = params.get("path")
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")
        create_dirs = params.get("create_dirs", True)
        
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        
        try:
            # Create directories if needed
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": file_path,
                "bytes_written": len(content.encode(encoding))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        dir_path = params.get("path", ".")
        recursive = params.get("recursive", False)
        include_hidden = params.get("include_hidden", False)
        pattern = params.get("pattern")
        
        try:
            if recursive:
                files = []
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        if not include_hidden and filename.startswith('.'):
                            continue
                        full_path = os.path.join(root, filename)
                        files.append({
                            "name": filename,
                            "path": full_path,
                            "type": "file",
                            "size": os.path.getsize(full_path)
                        })
            else:
                files = []
                for item in os.listdir(dir_path):
                    if not include_hidden and item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(dir_path, item)
                    item_type = "directory" if os.path.isdir(item_path) else "file"
                    size = os.path.getsize(item_path) if item_type == "file" else 0
                    
                    files.append({
                        "name": item,
                        "path": item_path,
                        "type": item_type,
                        "size": size
                    })
            
            # Apply pattern filter if provided
            if pattern:
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f["name"], pattern)]
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create directory"""
        dir_path = params.get("path")
        
        if not dir_path:
            return {"success": False, "error": "No directory path provided"}
        
        try:
            os.makedirs(dir_path, exist_ok=True)
            return {"success": True, "path": dir_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _find_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find files matching criteria"""
        search_path = params.get("path", ".")
        pattern = params.get("pattern", "*")
        content_search = params.get("content_search")
        max_results = params.get("max_results", 100)
        
        try:
            import fnmatch
            found_files = []
            
            for root, dirs, files in os.walk(search_path):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        file_path = os.path.join(root, filename)
                        
                        # Content search if specified
                        if content_search:
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if content_search.lower() not in content.lower():
                                        continue
                            except:
                                continue
                        
                        found_files.append({
                            "name": filename,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": os.path.getmtime(file_path)
                        })
                        
                        if len(found_files) >= max_results:
                            break
                
                if len(found_files) >= max_results:
                    break
            
            return {
                "success": True,
                "files": found_files,
                "count": len(found_files)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

class CodeGenerationAdapter(IntegrationAdapter):
    """Code generation and modification capabilities"""
    
    def __init__(self):
        super().__init__("code_generation")
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation operations"""
        
        try:
            if action == "generate_code":
                return await self._generate_code(params)
            elif action == "modify_code":
                return await self._modify_code(params)
            elif action == "analyze_code":
                return await self._analyze_code(params)
            elif action == "format_code":
                return await self._format_code(params)
            elif action == "extract_function":
                return await self._extract_function(params)
            elif action == "add_tests":
                return await self._add_tests(params)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"CodeGeneration adapter error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications"""
        specification = params.get("specification")
        language = params.get("language", "python")
        style = params.get("style", "standard")

        if not specification:
            return {"success": False, "error": "No specification provided"}

        try:
            # Lazy import to avoid heavy dependencies during module import
            global get_coding_agent  # type: ignore
            global jarvis_agent  # type: ignore
            if get_coding_agent is None or jarvis_agent is None:
                from jarvis import get_coding_agent as _get_coding_agent
                from jarvis.core.agent import jarvis_agent as _jarvis_agent
                get_coding_agent = _get_coding_agent
                jarvis_agent = _jarvis_agent

            coding_agent = get_coding_agent(jarvis_agent)
            generated_code = await asyncio.to_thread(
                coding_agent.generate_code, specification, language, style
            )

            return {
                "success": True,
                "code": generated_code,
                "language": language,
                "specification": specification,
                "style": style,
            }
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code structure and quality"""
        code = params.get("code")
        file_path = params.get("file_path")
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        
        if not code:
            return {"success": False, "error": "No code provided"}
        
        # Basic analysis
        lines = code.split('\n')
        
        analysis = {
            "line_count": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "function_count": len([line for line in lines if line.strip().startswith('def ')]),
            "class_count": len([line for line in lines if line.strip().startswith('class ')]),
            "complexity_estimate": "low"  # Basic estimation
        }
        
        return {
            "success": True,
            "analysis": analysis,
            "code_length": len(code)
        }

class TestingAdapter(IntegrationAdapter):
    """Testing automation and execution"""
    
    def __init__(self):
        super().__init__("testing")
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing operations"""
        
        try:
            if action == "run_tests":
                return await self._run_tests(params)
            elif action == "generate_tests":
                return await self._generate_tests(params)
            elif action == "analyze_coverage":
                return await self._analyze_coverage(params)
            elif action == "create_test_suite":
                return await self._create_test_suite(params)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Testing adapter error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run test suite"""
        test_path = params.get("test_path", ".")
        test_pattern = params.get("pattern", "test_*.py")
        verbose = params.get("verbose", False)
        
        try:
            # Run pytest if available
            cmd = ["python", "-m", "pytest", test_path]
            if verbose:
                cmd.append("-v")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test execution timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "pytest not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test cases for code."""
        code = params.get("code")
        file_path = params.get("file_path")
        test_type = params.get("test_type", "unit")

        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

        if not code:
            return {"success": False, "error": "No code provided"}

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {"success": False, "error": f"Invalid Python code: {exc}"}

        test_lines: List[str] = [
            "import unittest",
            "import types",
            f"SOURCE = {code!r}",
            "",
            "module = types.ModuleType('generated_module')",
            "exec(SOURCE, module.__dict__)",
            "",
            "class TestGeneratedCode(unittest.TestCase):",
            '    """Generated test cases for the provided code"""',
        ]

        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

        if not functions:
            test_lines.extend(
                [
                    "    def test_module_executes(self):",
                    "        self.assertIsNotNone(module)",
                    "",
                ]
            )
        else:
            for func in functions:
                name = func.name
                arg_count = len(func.args.args)
                args_call = ", ".join(["1"] * arg_count)
                call = f"module.{name}({args_call})" if arg_count else f"module.{name}()"
                test_lines.extend(
                    [
                        f"    def test_{name}_basic(self):",
                        f"        self.assertIsNotNone({call})",
                        "",
                        f"    def test_{name}_edge_case(self):",
                    ]
                )
                edge_args = ", ".join(["None"] * arg_count)
                edge_call = (
                    f"module.{name}({edge_args})" if arg_count else f"module.{name}(None)"
                )
                test_lines.extend(
                    [
                        "        with self.assertRaises(Exception):",
                        f"            {edge_call}",
                        "",
                    ]
                )

        test_lines.extend([
            "if __name__ == '__main__':",
            "    unittest.main()",
        ])

        test_code = "\n".join(test_lines)

        return {
            "success": True,
            "test_code": test_code,
            "test_type": test_type,
        }

class GitAdapter(IntegrationAdapter):
    """Git operations for version control"""
    
    def __init__(self):
        super().__init__("git")
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git operations"""
        
        try:
            if action == "status":
                return await self._git_status(params)
            elif action == "add":
                return await self._git_add(params)
            elif action == "commit":
                return await self._git_commit(params)
            elif action == "branch":
                return await self._git_branch(params)
            elif action == "diff":
                return await self._git_diff(params)
            elif action == "log":
                return await self._git_log(params)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Git adapter error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _git_command(self, cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
        """Execute git command"""
        try:
            result = subprocess.run(
                ["git"] + cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _git_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get git status"""
        repo_path = params.get("repo_path", ".")
        return await self._git_command(["status", "--porcelain"], repo_path)
    
    async def _git_add(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add files to git"""
        repo_path = params.get("repo_path", ".")
        files = params.get("files", ["."])
        
        if isinstance(files, str):
            files = [files]
        
        return await self._git_command(["add"] + files, repo_path)
    
    async def _git_commit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create git commit"""
        repo_path = params.get("repo_path", ".")
        message = params.get("message", "Automated commit")
        
        return await self._git_command(["commit", "-m", message], repo_path)

class IntegrationManager:
    """Manager for all integration adapters"""
    
    def __init__(self):
        self.adapters: Dict[str, IntegrationAdapter] = {}
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """Initialize all available adapters"""
        self.adapters["filesystem"] = FileSystemAdapter()
        self.adapters["code_generation"] = CodeGenerationAdapter()
        self.adapters["testing"] = TestingAdapter()
        self.adapters["git"] = GitAdapter()
    
    async def execute_integration(self, adapter_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration action through specified adapter"""
        
        if adapter_name not in self.adapters:
            return {"success": False, "error": f"Unknown adapter: {adapter_name}"}
        
        adapter = self.adapters[adapter_name]
        
        if not adapter.is_available():
            return {"success": False, "error": f"Adapter {adapter_name} is not available"}
        
        try:
            result = await adapter.execute(action, params)
            return result
        
        except Exception as e:
            logger.error(f"Integration execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_adapters(self) -> List[str]:
        """Get list of available adapters"""
        return [name for name, adapter in self.adapters.items() if adapter.is_available()]
    
    def get_adapter_info(self, adapter_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific adapter"""
        if adapter_name not in self.adapters:
            return None
        
        adapter = self.adapters[adapter_name]
        return {
            "name": adapter.name,
            "available": adapter.is_available(),
            "enabled": adapter.enabled
        }

# Global integration manager instance
integration_manager = IntegrationManager()

# Convenience functions for workflows
async def read_file(file_path: str) -> Dict[str, Any]:
    """Read file through integration manager"""
    return await integration_manager.execute_integration(
        "filesystem", "read_file", {"path": file_path}
    )

async def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write file through integration manager"""
    return await integration_manager.execute_integration(
        "filesystem", "write_file", {"path": file_path, "content": content}
    )

async def run_tests(test_path: str = ".") -> Dict[str, Any]:
    """Run tests through integration manager"""
    return await integration_manager.execute_integration(
        "testing", "run_tests", {"test_path": test_path}
    )

async def git_status(repo_path: str = ".") -> Dict[str, Any]:
    """Get git status through integration manager"""
    return await integration_manager.execute_integration(
        "git", "status", {"repo_path": repo_path}
    )

async def analyze_code(code: str = None, file_path: str = None) -> Dict[str, Any]:
    """Analyze code through integration manager"""
    params = {}
    if code:
        params["code"] = code
    if file_path:
        params["file_path"] = file_path
    
    return await integration_manager.execute_integration(
        "code_generation", "analyze_code", params
    )
