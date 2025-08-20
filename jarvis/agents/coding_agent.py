"""
Coding Agent - Advanced AI assistant for software development
"""

import logging
import json
import ast
import subprocess
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

class CodingAgent:
    """Advanced coding assistant with deep understanding capabilities"""
    
    def __init__(self, base_agent, workspace_path: str = None):
        self.base_agent = base_agent
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.conversation_context = []
        self.code_analysis_cache = {}
        
        # Coding-specific prompt templates
        self.system_prompts = {
            "code_review": """You are an expert code reviewer. Analyze the provided code for:
- Code quality and best practices
- Potential bugs and security issues
- Performance optimizations
- Documentation and readability
- Architecture and design patterns
Provide actionable feedback with specific examples.""",
            
            "debug_helper": """You are a debugging expert. Help identify and fix issues in code by:
- Analyzing error messages and stack traces
- Suggesting debugging strategies
- Identifying root causes
- Providing step-by-step solutions
- Recommending tools and techniques""",
            
            "code_generator": """You are a code generation specialist. Create high-quality code that:
- Follows best practices and conventions
- Includes proper error handling
- Has clear documentation
- Is well-structured and maintainable
- Includes relevant tests when appropriate""",
            
            "architecture_advisor": """You are a software architecture expert. Provide guidance on:
- System design and architecture patterns
- Technology stack recommendations
- Scalability and performance considerations
- Code organization and project structure
- Integration patterns and best practices""",
            
            "learning_mentor": """You are a coding mentor. Help developers learn by:
- Explaining concepts clearly with examples
- Providing step-by-step guidance
- Suggesting learning resources
- Offering practice exercises
- Encouraging best practices"""
        }
    
    def analyze_codebase(self, directory: str = None) -> Dict[str, Any]:
        """Analyze the current codebase for context"""
        target_dir = Path(directory) if directory else self.workspace_path
        
        analysis = {
            "languages": {},
            "structure": {},
            "dependencies": [],
            "complexity_metrics": {},
            "recent_changes": []
        }
        
        try:
            # Language detection
            for file_path in target_dir.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.rb']:
                        lang = self._get_language_from_extension(ext)
                        analysis["languages"][lang] = analysis["languages"].get(lang, 0) + 1
            
            # Project structure
            analysis["structure"] = self._analyze_project_structure(target_dir)
            
            # Dependencies
            analysis["dependencies"] = self._extract_dependencies(target_dir)
            
            logger.info(f"Analyzed codebase: {len(analysis['languages'])} languages detected")
            
        except Exception as e:
            logger.error(f"Error analyzing codebase: {e}")
        
        return analysis
    
    def code_review(self, code: str, language: str = "python", context: str = "") -> str:
        """Perform comprehensive code review"""
        prompt = f"""
{self.system_prompts['code_review']}

Language: {language}
Context: {context}

Code to review:
```{language}
{code}
```

Please provide a detailed code review with specific recommendations.
"""
        
        response = self.base_agent.chat(prompt)
        self._add_to_context("code_review", {"code": code[:200], "language": language, "response": response[:100]})
        return response
    
    def debug_assistance(self, error_message: str, code: str = "", language: str = "python") -> str:
        """Help debug code issues"""
        prompt = f"""
{self.system_prompts['debug_helper']}

Language: {language}
Error message: {error_message}

{"Code context:" if code else ""}
{f"```{language}\n{code}\n```" if code else ""}

Please help identify the issue and provide a solution.
"""
        
        response = self.base_agent.chat(prompt)
        self._add_to_context("debug", {"error": error_message, "language": language})
        return response
    
    def generate_code(self, requirements: str, language: str = "python", style: str = "modern") -> str:
        """Generate code based on requirements"""
        codebase_context = self.analyze_codebase()
        
        prompt = f"""
{self.system_prompts['code_generator']}

Requirements: {requirements}
Language: {language}
Style: {style}

Project context:
- Languages in use: {list(codebase_context['languages'].keys())}
- Project type: {self._infer_project_type(codebase_context)}

Please generate clean, well-documented code that meets the requirements.
"""
        
        response = self.base_agent.chat(prompt)
        self._add_to_context("code_generation", {"requirements": requirements, "language": language})
        return response
    
    def architecture_advice(self, question: str, project_context: str = "") -> str:
        """Provide software architecture guidance"""
        codebase_analysis = self.analyze_codebase()
        
        prompt = f"""
{self.system_prompts['architecture_advisor']}

Question: {question}
Project context: {project_context}

Current codebase analysis:
- Languages: {codebase_analysis['languages']}
- Structure: {codebase_analysis['structure']}
- Dependencies: {codebase_analysis['dependencies'][:5]}

Please provide architectural guidance based on the current project context.
"""
        
        response = self.base_agent.chat(prompt)
        self._add_to_context("architecture", {"question": question})
        return response
    
    def explain_code(self, code: str, language: str = "python", level: str = "intermediate") -> str:
        """Explain how code works"""
        prompt = f"""
{self.system_prompts['learning_mentor']}

Explanation level: {level}
Language: {language}

Code to explain:
```{language}
{code}
```

Please explain how this code works, breaking it down step by step.
"""
        
        response = self.base_agent.chat(prompt)
        self._add_to_context("explanation", {"language": language, "level": level})
        return response
    
    def suggest_improvements(self, code: str, language: str = "python", focus: str = "performance") -> str:
        """Suggest code improvements"""
        prompt = f"""
{self.system_prompts['code_review']}

Focus area: {focus}
Language: {language}

Code to improve:
```{language}
{code}
```

Please suggest specific improvements focusing on {focus}. Provide before/after examples where helpful.
"""
        
        response = self.base_agent.chat(prompt)
        return response
    
    def create_tests(self, code: str, language: str = "python", test_framework: str = "pytest") -> str:
        """Generate test cases for code"""
        prompt = f"""
You are a test automation expert. Create comprehensive test cases for the provided code.

Language: {language}
Test framework: {test_framework}

Code to test:
```{language}
{code}
```

Please generate:
1. Unit tests covering main functionality
2. Edge cases and error conditions
3. Integration tests if applicable
4. Mock objects where needed

Follow {test_framework} best practices.
"""
        
        response = self.base_agent.chat(prompt)
        return response
    
    def refactor_code(self, code: str, language: str = "python", pattern: str = "clean_code") -> str:
        """Refactor code following specific patterns"""
        prompt = f"""
You are a refactoring expert. Refactor the provided code following {pattern} principles.

Language: {language}
Target pattern: {pattern}

Original code:
```{language}
{code}
```

Please refactor this code to:
- Improve readability and maintainability
- Follow {pattern} principles
- Preserve functionality
- Add appropriate comments
- Extract methods/functions where beneficial
"""
        
        response = self.base_agent.chat(prompt)
        return response
    
    def performance_analysis(self, code: str, language: str = "python") -> str:
        """Analyze code performance and suggest optimizations"""
        prompt = f"""
You are a performance optimization expert. Analyze the provided code for performance issues.

Language: {language}

Code to analyze:
```{language}
{code}
```

Please analyze:
1. Time complexity (Big O notation)
2. Space complexity
3. Potential bottlenecks
4. Optimization opportunities
5. Profiling recommendations

Provide specific optimization suggestions with examples.
"""
        
        response = self.base_agent.chat(prompt)
        return response
    
    def _get_language_from_extension(self, ext: str) -> str:
        """Map file extensions to language names"""
        mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby'
        }
        return mapping.get(ext, 'Unknown')
    
    def _analyze_project_structure(self, directory: Path) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            "type": "unknown",
            "framework": None,
            "directories": [],
            "config_files": []
        }
        
        # Check for common project indicators
        for item in directory.iterdir():
            if item.is_dir():
                structure["directories"].append(item.name)
            elif item.is_file():
                name = item.name.lower()
                if name in ['package.json', 'requirements.txt', 'pyproject.toml', 'Cargo.toml', 'pom.xml']:
                    structure["config_files"].append(name)
        
        # Infer project type
        if 'package.json' in structure["config_files"]:
            structure["type"] = "Node.js"
        elif any(f in structure["config_files"] for f in ['requirements.txt', 'pyproject.toml']):
            structure["type"] = "Python"
        elif 'Cargo.toml' in structure["config_files"]:
            structure["type"] = "Rust"
        
        return structure
    
    def _extract_dependencies(self, directory: Path) -> List[str]:
        """Extract project dependencies"""
        dependencies = []
        
        # Python dependencies
        req_file = directory / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    dependencies.extend([line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')])
            except Exception as e:
                logger.warning(f"Error reading requirements.txt: {e}")
        
        # Node.js dependencies
        package_json = directory / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dependencies.extend(list(deps.keys()))
            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")
        
        return dependencies[:20]  # Limit to first 20
    
    def _infer_project_type(self, analysis: Dict[str, Any]) -> str:
        """Infer the type of project based on analysis"""
        if analysis["structure"]["type"] != "unknown":
            return analysis["structure"]["type"]
        
        # Fallback to language detection
        languages = analysis["languages"]
        if not languages:
            return "Unknown"
        
        most_common = max(languages, key=languages.get)
        return f"{most_common} project"
    
    def analyze_specific_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze specific files for context"""
        analysis = {
            "files": {},
            "total_lines": 0,
            "languages": {},
            "imports": [],
            "functions": [],
            "classes": []
        }
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                continue
                
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_info = {
                    "lines": len(content.splitlines()),
                    "size": len(content),
                    "language": self._get_language_from_extension(path.suffix)
                }
                
                # Basic code analysis for Python files
                if path.suffix == '.py':
                    file_info.update(self._analyze_python_file(content))
                
                analysis["files"][str(path)] = file_info
                analysis["total_lines"] += file_info["lines"]
                
                lang = file_info["language"]
                analysis["languages"][lang] = analysis["languages"].get(lang, 0) + 1
                
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {e}")
        
        return analysis
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file for imports, functions, classes"""
        info = {
            "imports": [],
            "functions": [],
            "classes": [],
            "docstrings": 0
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    info["imports"].append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    info["functions"].append(node.name)
                    if ast.get_docstring(node):
                        info["docstrings"] += 1
                elif isinstance(node, ast.ClassDef):
                    info["classes"].append(node.name)
                    if ast.get_docstring(node):
                        info["docstrings"] += 1
                        
        except SyntaxError:
            # File has syntax errors
            pass
        except Exception as e:
            logger.warning(f"Error parsing Python file: {e}")
        
        return info
    
    def analyze_file_content(self, file_path: str) -> str:
        """Analyze a specific file and provide insights"""
        path = Path(file_path)
        if not path.exists():
            return f"File {file_path} does not exist."
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self._get_language_from_extension(path.suffix)
            analysis = self.analyze_specific_files([file_path])
            file_info = analysis["files"].get(str(path), {})
            
            prompt = f"""
You are a code analysis expert. Analyze this {language} file and provide insights:

File: {path.name}
Lines: {file_info.get('lines', 'unknown')}
Language: {language}

Code:
```{language.lower()}
{content[:5000]}{'...' if len(content) > 5000 else ''}
```

Please provide:
1. Purpose and functionality summary
2. Code quality assessment
3. Potential improvements
4. Dependencies and imports analysis
5. Architecture patterns used
"""
            
            return self.base_agent.chat(prompt)
            
        except Exception as e:
            return f"Error analyzing file: {e}"
    
    def _add_to_context(self, action_type: str, data: Dict[str, Any]):
        """Add interaction to conversation context"""
        self.conversation_context.append({
            "type": action_type,
            "data": data,
            "timestamp": None  # Could add actual timestamp
        })
        
        # Keep context manageable
        if len(self.conversation_context) > 50:
            self.conversation_context = self.conversation_context[-30:]
    
    def get_coding_capabilities(self) -> Dict[str, List[str]]:
        """Return available coding assistance capabilities"""
        return {
            "code_analysis": [
                "Code review and quality assessment",
                "Performance analysis and optimization",
                "Security vulnerability detection",
                "Best practices validation"
            ],
            "code_generation": [
                "Function and class generation",
                "Test case creation",
                "Documentation generation",
                "Boilerplate code creation"
            ],
            "debugging": [
                "Error analysis and solutions",
                "Stack trace interpretation",
                "Bug identification and fixes",
                "Debugging strategy suggestions"
            ],
            "refactoring": [
                "Code structure improvement",
                "Design pattern implementation",
                "Performance optimization",
                "Maintainability enhancement"
            ],
            "learning": [
                "Code explanation and teaching",
                "Concept clarification",
                "Best practice guidance",
                "Technology recommendations"
            ],
            "architecture": [
                "System design advice",
                "Technology stack suggestions",
                "Scalability planning",
                "Integration patterns"
            ]
        }

# Global instance
_coding_agent = None

def get_coding_agent(base_agent, workspace_path: str = None) -> CodingAgent:
    """Get global coding agent instance"""
    global _coding_agent
    if _coding_agent is None:
        _coding_agent = CodingAgent(base_agent, workspace_path)
    return _coding_agent
