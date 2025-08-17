"""
Code Review Module
Provides automated code review capabilities including style checking, 
best practices validation, and security analysis.
"""
import os
import re
import ast
import subprocess
from typing import List, Dict, Any, Optional


class CodeReviewer:
    def __init__(self):
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs'}
    
    def review_code(self, file_path: str, check_types: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive code review on a file.
        
        Args:
            file_path: Path to the code file
            check_types: List of check types to perform ['style', 'security', 'complexity', 'best_practices']
                        If None, performs all checks
        
        Returns:
            Dictionary containing review results
        """
        if check_types is None:
            check_types = ['style', 'security', 'complexity', 'best_practices']
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_extensions:
            return {"error": f"Unsupported file type: {ext}"}
        
        results = {
            "file": file_path,
            "extension": ext,
            "checks_performed": check_types,
            "issues": [],
            "suggestions": [],
            "metrics": {},
            "overall_score": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Perform requested checks
            if 'style' in check_types:
                style_issues = self._check_style(content, ext)
                results["issues"].extend(style_issues)
            
            if 'security' in check_types:
                security_issues = self._check_security(content, ext)
                results["issues"].extend(security_issues)
            
            if 'complexity' in check_types:
                complexity_metrics = self._analyze_complexity(content, ext)
                results["metrics"].update(complexity_metrics)
            
            if 'best_practices' in check_types:
                best_practice_suggestions = self._check_best_practices(content, ext)
                results["suggestions"].extend(best_practice_suggestions)
            
            # Calculate overall score
            results["overall_score"] = self._calculate_score(results)
            
        except Exception as e:
            results["error"] = f"Error analyzing file: {str(e)}"
        
        return results
    
    def _check_style(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Check code style issues."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Common style checks across languages
            if len(line.strip()) > 120:
                issues.append({
                    "type": "style",
                    "severity": "minor",
                    "line": i,
                    "message": "Line too long (>120 characters)",
                    "suggestion": "Consider breaking long lines"
                })
            
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "type": "style",
                    "severity": "minor",
                    "line": i,
                    "message": "Trailing whitespace",
                    "suggestion": "Remove trailing whitespace"
                })
        
        # Python-specific style checks
        if ext == '.py':
            issues.extend(self._check_python_style(content, lines))
        
        return issues
    
    def _check_python_style(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Python-specific style checks."""
        issues = []
        
        # Check for proper import organization
        import_pattern = re.compile(r'^(import|from)\s+')
        imports_section = True
        first_non_import_line = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            if import_pattern.match(stripped):
                if not imports_section and first_non_import_line > 0:
                    issues.append({
                        "type": "style",
                        "severity": "minor",
                        "line": i,
                        "message": "Import after non-import statement",
                        "suggestion": "Move imports to top of file"
                    })
            else:
                if imports_section:
                    imports_section = False
                    first_non_import_line = i
        
        # Check for function/class naming conventions
        function_pattern = re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
        class_pattern = re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        
        for i, line in enumerate(lines, 1):
            # Function naming (should be snake_case)
            func_match = function_pattern.search(line)
            if func_match:
                func_name = func_match.group(1)
                if not func_name.islower() and '_' not in func_name and not func_name.startswith('_'):
                    if any(c.isupper() for c in func_name):
                        issues.append({
                            "type": "style",
                            "severity": "minor",
                            "line": i,
                            "message": f"Function '{func_name}' should use snake_case",
                            "suggestion": "Use snake_case for function names"
                        })
            
            # Class naming (should be PascalCase)
            class_match = class_pattern.search(line)
            if class_match:
                class_name = class_match.group(1)
                if not class_name[0].isupper():
                    issues.append({
                        "type": "style",
                        "severity": "minor",
                        "line": i,
                        "message": f"Class '{class_name}' should use PascalCase",
                        "suggestion": "Use PascalCase for class names"
                    })
        
        return issues
    
    def _check_security(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Check for potential security issues."""
        issues = []
        lines = content.split('\n')
        
        # Common security patterns
        security_patterns = {
            'hardcoded_password': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'cursor\.execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*=\s*["\'].*\+.*["\']'
            ],
            'shell_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\('
            ]
        }
        
        for i, line in enumerate(lines, 1):
            for issue_type, patterns in security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            "type": "security",
                            "severity": "major",
                            "line": i,
                            "message": f"Potential {issue_type.replace('_', ' ')} vulnerability",
                            "suggestion": f"Review {issue_type.replace('_', ' ')} usage for security"
                        })
        
        return issues
    
    def _analyze_complexity(self, content: str, ext: str) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        metrics = {
            "lines_of_code": len(content.split('\n')),
            "non_empty_lines": len([line for line in content.split('\n') if line.strip()]),
            "comment_lines": 0,
            "functions": 0,
            "classes": 0,
            "max_line_length": 0,
            "cyclomatic_complexity": 0
        }
        
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                metrics["comment_lines"] += 1
            
            metrics["max_line_length"] = max(metrics["max_line_length"], len(line))
        
        # Language-specific complexity analysis
        if ext == '.py':
            metrics.update(self._analyze_python_complexity(content))
        
        return metrics
    
    def _analyze_python_complexity(self, content: str) -> Dict[str, Any]:
        """Python-specific complexity analysis."""
        metrics = {"functions": 0, "classes": 0, "cyclomatic_complexity": 0}
        
        try:
            tree = ast.parse(content)
            
            class ComplexityAnalyzer(ast.NodeVisitor):
                def __init__(self):
                    self.functions = 0
                    self.classes = 0
                    self.complexity = 1  # Base complexity
                
                def visit_FunctionDef(self, node):
                    self.functions += 1
                    self.generic_visit(node)
                
                def visit_ClassDef(self, node):
                    self.classes += 1
                    self.generic_visit(node)
                
                def visit_If(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_For(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_While(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_Try(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
            
            analyzer = ComplexityAnalyzer()
            analyzer.visit(tree)
            
            metrics["functions"] = analyzer.functions
            metrics["classes"] = analyzer.classes
            metrics["cyclomatic_complexity"] = analyzer.complexity
            
        except SyntaxError:
            pass  # Invalid Python syntax
        
        return metrics
    
    def _check_best_practices(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Check for best practice violations."""
        suggestions = []
        
        # Common best practices
        if ext == '.py':
            suggestions.extend(self._check_python_best_practices(content))
        
        return suggestions
    
    def _check_python_best_practices(self, content: str) -> List[Dict[str, Any]]:
        """Python-specific best practice checks."""
        suggestions = []
        lines = content.split('\n')
        
        # Check for docstrings in functions/classes
        function_pattern = re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
        class_pattern = re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        
        for i, line in enumerate(lines):
            if function_pattern.search(line) or class_pattern.search(line):
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines) and not (lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''")):
                    suggestions.append({
                        "type": "best_practice",
                        "severity": "minor",
                        "line": i + 1,
                        "message": "Missing docstring",
                        "suggestion": "Add docstring to document purpose and parameters"
                    })
        
        # Check for bare except clauses
        for i, line in enumerate(lines, 1):
            if re.search(r'except\s*:', line):
                suggestions.append({
                    "type": "best_practice",
                    "severity": "major",
                    "line": i,
                    "message": "Bare except clause",
                    "suggestion": "Specify exception types to catch"
                })
        
        return suggestions
    
    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall code quality score (0-100)."""
        base_score = 100
        
        # Deduct points for issues
        for issue in results["issues"]:
            if issue["severity"] == "major":
                base_score -= 10
            elif issue["severity"] == "minor":
                base_score -= 2
        
        # Deduct points for suggestions
        base_score -= len(results["suggestions"]) * 1
        
        # Adjust for complexity
        metrics = results.get("metrics", {})
        complexity = metrics.get("cyclomatic_complexity", 0)
        if complexity > 20:
            base_score -= 15
        elif complexity > 10:
            base_score -= 5
        
        return max(0, base_score)


def review_file(file_path: str, check_types: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function to review a single file.
    
    Args:
        file_path: Path to the file to review
        check_types: Types of checks to perform
    
    Returns:
        Review results dictionary
    """
    reviewer = CodeReviewer()
    return reviewer.review_code(file_path, check_types)


def review_directory(directory_path: str, recursive: bool = True, 
                    check_types: List[str] = None) -> Dict[str, Any]:
    """
    Review all code files in a directory.
    
    Args:
        directory_path: Path to directory to review
        recursive: Whether to review subdirectories
        check_types: Types of checks to perform
    
    Returns:
        Combined review results for all files
    """
    reviewer = CodeReviewer()
    results = {
        "directory": directory_path,
        "files_reviewed": [],
        "total_issues": 0,
        "total_suggestions": 0,
        "average_score": 0
    }
    
    if not os.path.exists(directory_path):
        results["error"] = f"Directory not found: {directory_path}"
        return results
    
    scores = []
    
    # Get all code files
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext in reviewer.supported_extensions:
                file_results = reviewer.review_code(file_path, check_types)
                if "error" not in file_results:
                    results["files_reviewed"].append(file_results)
                    results["total_issues"] += len(file_results["issues"])
                    results["total_suggestions"] += len(file_results["suggestions"])
                    scores.append(file_results["overall_score"])
        
        if not recursive:
            break
    
    if scores:
        results["average_score"] = sum(scores) / len(scores)
    
    return results