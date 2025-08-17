"""
Repository Context Module
Provides comprehensive repository context for LLM/RAG tasks including
project structure, dependencies, git history, and code patterns.
"""
import os
import git
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import fnmatch
from datetime import datetime, timedelta


class RepositoryContext:
    def __init__(self, repo_path: str = None):
        """
        Initialize repository context analyzer.
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        self._init_git_repo()
        
        # Common patterns to ignore
        self.ignore_patterns = {
            'directories': [
                '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
                '.idea', '.vscode', 'dist', 'build', '.pytest_cache', '.coverage',
                '.mypy_cache', '.tox', 'htmlcov'
            ],
            'files': [
                '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
                '*.log', '*.tmp', '*.temp', '*.swp', '*.swo', '*~',
                '.DS_Store', 'Thumbs.db', '*.egg-info'
            ]
        }
    
    def _init_git_repo(self):
        """Initialize git repository object."""
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
    
    def get_project_structure(self, max_depth: int = 5, include_files: bool = True) -> Dict[str, Any]:
        """
        Get project directory structure.
        
        Args:
            max_depth: Maximum directory depth to traverse
            include_files: Whether to include files in the structure
        
        Returns:
            Project structure information
        """
        structure = {
            "root": self.repo_path,
            "tree": {},
            "summary": {
                "total_directories": 0,
                "total_files": 0,
                "file_types": {},
                "largest_files": [],
                "recent_files": []
            }
        }
        
        def should_ignore(path: str, is_dir: bool) -> bool:
            name = os.path.basename(path)
            
            if is_dir:
                return name in self.ignore_patterns['directories']
            else:
                return any(fnmatch.fnmatch(name, pattern) 
                          for pattern in self.ignore_patterns['files'])
        
        def build_tree(current_path: str, current_depth: int) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {}
            
            tree = {}
            
            try:
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    
                    if should_ignore(item_path, os.path.isdir(item_path)):
                        continue
                    
                    if os.path.isdir(item_path):
                        structure["summary"]["total_directories"] += 1
                        tree[item] = {
                            "type": "directory",
                            "children": build_tree(item_path, current_depth + 1)
                        }
                    elif include_files:
                        structure["summary"]["total_files"] += 1
                        
                        # File statistics
                        try:
                            stat = os.stat(item_path)
                            file_size = stat.st_size
                            mod_time = datetime.fromtimestamp(stat.st_mtime)
                            
                            # Track file types
                            ext = os.path.splitext(item)[1].lower()
                            if ext:
                                structure["summary"]["file_types"][ext] = structure["summary"]["file_types"].get(ext, 0) + 1
                            
                            # Track large files
                            if file_size > 1024 * 1024:  # > 1MB
                                structure["summary"]["largest_files"].append({
                                    "path": os.path.relpath(item_path, self.repo_path),
                                    "size": file_size,
                                    "size_mb": round(file_size / (1024 * 1024), 2)
                                })
                            
                            # Track recent files (modified in last 7 days)
                            if mod_time > datetime.now() - timedelta(days=7):
                                structure["summary"]["recent_files"].append({
                                    "path": os.path.relpath(item_path, self.repo_path),
                                    "modified": mod_time.isoformat(),
                                    "size": file_size
                                })
                            
                            tree[item] = {
                                "type": "file",
                                "size": file_size,
                                "modified": mod_time.isoformat(),
                                "extension": ext
                            }
                        except OSError:
                            tree[item] = {"type": "file", "error": "Cannot access"}
            
            except PermissionError:
                pass
            
            return tree
        
        structure["tree"] = build_tree(self.repo_path, 0)
        
        # Sort largest files by size
        structure["summary"]["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        structure["summary"]["largest_files"] = structure["summary"]["largest_files"][:10]
        
        # Sort recent files by modification time
        structure["summary"]["recent_files"].sort(key=lambda x: x["modified"], reverse=True)
        structure["summary"]["recent_files"] = structure["summary"]["recent_files"][:20]
        
        return structure
    
    def get_git_context(self) -> Dict[str, Any]:
        """Get git repository context."""
        if not self.repo:
            return {"error": "Not a git repository"}
        
        context = {
            "repository_info": {},
            "branches": [],
            "recent_commits": [],
            "current_status": {},
            "remote_info": []
        }
        
        try:
            # Repository basic info
            context["repository_info"] = {
                "working_dir": self.repo.working_dir,
                "git_dir": self.repo.git_dir,
                "active_branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "bare": self.repo.bare
            }
            
            # Branches
            context["branches"] = [
                {
                    "name": branch.name,
                    "is_active": branch == self.repo.active_branch,
                    "commit": str(branch.commit)[:8]
                }
                for branch in self.repo.branches
            ]
            
            # Recent commits (last 10)
            commits = list(self.repo.iter_commits(max_count=10))
            context["recent_commits"] = [
                {
                    "sha": str(commit)[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                }
                for commit in commits
            ]
            
            # Current status
            if self.repo.is_dirty():
                context["current_status"] = {
                    "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                    "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                    "untracked_files": self.repo.untracked_files
                }
            
            # Remote information
            for remote in self.repo.remotes:
                context["remote_info"].append({
                    "name": remote.name,
                    "url": remote.url if hasattr(remote, 'url') else "Unknown",
                    "refs": [ref.name for ref in remote.refs] if remote.refs else []
                })
        
        except Exception as e:
            context["error"] = f"Error getting git context: {str(e)}"
        
        return context
    
    def get_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            "python": {"files": [], "packages": []},
            "javascript": {"files": [], "packages": []},
            "other": {"files": []}
        }
        
        # Python dependencies
        python_files = [
            "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
            "Pipfile", "pyproject.toml", "setup.py", "setup.cfg"
        ]
        
        for file in python_files:
            file_path = os.path.join(self.repo_path, file)
            if os.path.exists(file_path):
                dependencies["python"]["files"].append(file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if file == "requirements.txt" or file.startswith("requirements"):
                        # Parse requirements.txt format
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                                if package:
                                    dependencies["python"]["packages"].append(package)
                    
                    elif file == "pyproject.toml":
                        # Basic parsing for pyproject.toml
                        import re
                        packages = re.findall(r'"([^"]+)"', content)
                        dependencies["python"]["packages"].extend(packages)
                
                except Exception:
                    pass  # Skip files that can't be read
        
        # JavaScript dependencies
        js_files = ["package.json", "package-lock.json", "yarn.lock"]
        
        for file in js_files:
            file_path = os.path.join(self.repo_path, file)
            if os.path.exists(file_path):
                dependencies["javascript"]["files"].append(file)
                
                if file == "package.json":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            package_data = json.load(f)
                        
                        # Get dependencies
                        for dep_type in ["dependencies", "devDependencies"]:
                            if dep_type in package_data:
                                dependencies["javascript"]["packages"].extend(
                                    package_data[dep_type].keys()
                                )
                    except Exception:
                        pass
        
        # Other dependency files
        other_files = [
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            "Makefile", "CMakeLists.txt", "build.gradle", "pom.xml"
        ]
        
        for file in other_files:
            if os.path.exists(os.path.join(self.repo_path, file)):
                dependencies["other"]["files"].append(file)
        
        return dependencies
    
    def get_code_patterns(self) -> Dict[str, Any]:
        """Analyze common code patterns and conventions."""
        patterns = {
            "languages": {},
            "frameworks": [],
            "patterns": {},
            "conventions": {}
        }
        
        # Count file types and detect languages
        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns['directories']]
            
            for file in files:
                if any(fnmatch.fnmatch(file, pattern) for pattern in self.ignore_patterns['files']):
                    continue
                
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    patterns["languages"][ext] = patterns["languages"].get(ext, 0) + 1
        
        # Detect frameworks and libraries based on file patterns
        framework_indicators = {
            "Django": ["manage.py", "settings.py", "urls.py"],
            "Flask": ["app.py", "wsgi.py"],
            "FastAPI": ["main.py"],
            "React": ["package.json", "src/App.js", "src/index.js"],
            "Vue": ["vue.config.js", "src/main.js"],
            "Angular": ["angular.json", "src/app/app.module.ts"],
            "Spring": ["pom.xml", "src/main/java"],
            "Express": ["package.json", "server.js", "app.js"]
        }
        
        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                if os.path.exists(os.path.join(self.repo_path, indicator)):
                    patterns["frameworks"].append(framework)
                    break
        
        # Analyze Python code patterns (if Python files exist)
        if '.py' in patterns["languages"]:
            patterns["patterns"]["python"] = self._analyze_python_patterns()
        
        return patterns
    
    def _analyze_python_patterns(self) -> Dict[str, Any]:
        """Analyze Python-specific patterns."""
        python_patterns = {
            "imports": {},
            "classes": 0,
            "functions": 0,
            "decorators": [],
            "async_usage": 0
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns['directories']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Count imports
                        import re
                        imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+([^\n]+)', content, re.MULTILINE)
                        for module, items in imports:
                            base_module = (module or items.split()[0]).split('.')[0]
                            python_patterns["imports"][base_module] = python_patterns["imports"].get(base_module, 0) + 1
                        
                        # Count classes and functions
                        python_patterns["classes"] += len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
                        python_patterns["functions"] += len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
                        
                        # Find decorators
                        decorators = re.findall(r'@(\w+)', content)
                        python_patterns["decorators"].extend(decorators)
                        
                        # Count async usage
                        python_patterns["async_usage"] += len(re.findall(r'\basync\s+def\b', content))
                        python_patterns["async_usage"] += len(re.findall(r'\bawait\b', content))
                    
                    except Exception:
                        continue
        
        # Get unique decorators
        python_patterns["decorators"] = list(set(python_patterns["decorators"]))
        
        return python_patterns
    
    def get_documentation_files(self) -> List[Dict[str, Any]]:
        """Find and analyze documentation files."""
        doc_files = []
        
        # Common documentation file patterns
        doc_patterns = {
            'README': ['README*', 'readme*'],
            'CHANGELOG': ['CHANGELOG*', 'changelog*', 'HISTORY*'],
            'LICENSE': ['LICENSE*', 'COPYING*'],
            'CONTRIBUTING': ['CONTRIBUTING*'],
            'DOCS': ['docs/', 'documentation/', 'doc/'],
            'API': ['api.md', 'API.md', 'api.rst']
        }
        
        for doc_type, patterns in doc_patterns.items():
            for pattern in patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    dir_path = os.path.join(self.repo_path, pattern)
                    if os.path.isdir(dir_path):
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                if file.endswith(('.md', '.rst', '.txt', '.html')):
                                    file_path = os.path.join(root, file)
                                    rel_path = os.path.relpath(file_path, self.repo_path)
                                    doc_files.append({
                                        'type': doc_type,
                                        'path': rel_path,
                                        'name': file,
                                        'size': os.path.getsize(file_path)
                                    })
                else:
                    # File pattern
                    import glob
                    matches = glob.glob(os.path.join(self.repo_path, pattern))
                    for match in matches:
                        if os.path.isfile(match):
                            rel_path = os.path.relpath(match, self.repo_path)
                            doc_files.append({
                                'type': doc_type,
                                'path': rel_path,
                                'name': os.path.basename(match),
                                'size': os.path.getsize(match)
                            })
        
        return doc_files
    
    def get_comprehensive_context(self) -> Dict[str, Any]:
        """Get comprehensive repository context for LLM/RAG."""
        context = {
            "repository_path": self.repo_path,
            "timestamp": datetime.now().isoformat(),
            "project_structure": self.get_project_structure(max_depth=3, include_files=False),
            "git_context": self.get_git_context(),
            "dependencies": self.get_dependencies(),
            "code_patterns": self.get_code_patterns(),
            "documentation": self.get_documentation_files()
        }
        
        # Add summary for LLM consumption
        context["summary"] = self._generate_context_summary(context)
        
        return context
    
    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the repository context."""
        summary_parts = []
        
        # Repository basics
        repo_info = context.get("git_context", {}).get("repository_info", {})
        if repo_info:
            active_branch = repo_info.get("active_branch", "unknown")
            is_dirty = repo_info.get("is_dirty", False)
            summary_parts.append(f"Repository on branch '{active_branch}'" + 
                                (" (dirty)" if is_dirty else " (clean)"))
        
        # Project structure
        structure = context.get("project_structure", {}).get("summary", {})
        if structure:
            total_files = structure.get("total_files", 0)
            total_dirs = structure.get("total_directories", 0)
            summary_parts.append(f"Project contains {total_files} files in {total_dirs} directories")
            
            # File types
            file_types = structure.get("file_types", {})
            if file_types:
                top_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]
                type_summary = ", ".join([f"{ext}: {count}" for ext, count in top_types])
                summary_parts.append(f"Main file types: {type_summary}")
        
        # Languages and frameworks
        patterns = context.get("code_patterns", {})
        languages = patterns.get("languages", {})
        if languages:
            top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_summary = ", ".join([f"{ext[1:] if ext.startswith('.') else ext}" for ext, _ in top_langs])
            summary_parts.append(f"Primary languages: {lang_summary}")
        
        frameworks = patterns.get("frameworks", [])
        if frameworks:
            summary_parts.append(f"Frameworks detected: {', '.join(frameworks)}")
        
        # Dependencies
        deps = context.get("dependencies", {})
        dep_summary = []
        if deps.get("python", {}).get("files"):
            dep_summary.append("Python")
        if deps.get("javascript", {}).get("files"):
            dep_summary.append("JavaScript/Node.js")
        if dep_summary:
            summary_parts.append(f"Dependency management: {', '.join(dep_summary)}")
        
        # Recent activity
        git_ctx = context.get("git_context", {})
        recent_commits = git_ctx.get("recent_commits", [])
        if recent_commits:
            latest = recent_commits[0]
            summary_parts.append(f"Latest commit: {latest.get('message', 'No message')[:50]}")
        
        return ". ".join(summary_parts) + "."


def get_repository_context(repo_path: str = None) -> Dict[str, Any]:
    """
    Convenience function to get comprehensive repository context.
    
    Args:
        repo_path: Path to repository (defaults to current directory)
    
    Returns:
        Repository context information
    """
    context_analyzer = RepositoryContext(repo_path)
    return context_analyzer.get_comprehensive_context()


def format_context_for_llm(context: Dict[str, Any], max_length: int = 4000) -> str:
    """
    Format repository context for LLM consumption.
    
    Args:
        context: Repository context from get_repository_context()
        max_length: Maximum length of formatted text
    
    Returns:
        Formatted context string for LLM
    """
    formatted = []
    
    # Summary
    summary = context.get("summary", "")
    if summary:
        formatted.append(f"REPOSITORY OVERVIEW:\n{summary}\n")
    
    # Current git status
    git_ctx = context.get("git_context", {})
    status = git_ctx.get("current_status", {})
    if status:
        formatted.append("CURRENT CHANGES:")
        if status.get("modified_files"):
            formatted.append(f"Modified: {', '.join(status['modified_files'][:5])}")
        if status.get("staged_files"):
            formatted.append(f"Staged: {', '.join(status['staged_files'][:5])}")
        if status.get("untracked_files"):
            formatted.append(f"Untracked: {', '.join(status['untracked_files'][:5])}")
        formatted.append("")
    
    # Recent commits
    recent_commits = git_ctx.get("recent_commits", [])
    if recent_commits:
        formatted.append("RECENT COMMITS:")
        for commit in recent_commits[:3]:
            formatted.append(f"- {commit.get('message', 'No message')[:80]} ({commit.get('sha', 'unknown')})")
        formatted.append("")
    
    # Dependencies
    deps = context.get("dependencies", {})
    if any(deps.values()):
        formatted.append("DEPENDENCIES:")
        for lang, info in deps.items():
            if info.get("files"):
                formatted.append(f"- {lang.title()}: {', '.join(info['files'])}")
        formatted.append("")
    
    # Documentation
    docs = context.get("documentation", [])
    if docs:
        formatted.append("DOCUMENTATION:")
        for doc in docs[:5]:
            formatted.append(f"- {doc['type']}: {doc['path']}")
        formatted.append("")
    
    result = "\n".join(formatted)
    
    # Truncate if too long
    if len(result) > max_length:
        result = result[:max_length - 20] + "\n...(truncated)"
    
    return result