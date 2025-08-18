"""
Test Generation and Coverage Analysis Module
Provides automated test generation, coverage analysis, and test quality assessment.
"""
import os
import ast
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import importlib.util


class TestGenerator:
    def __init__(self, repository_path: str = None):
        self.repository_path = repository_path or os.getcwd()
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}
        self.test_frameworks = {
            '.py': ['pytest', 'unittest'],
            '.js': ['jest', 'mocha'],
            '.ts': ['jest', 'vitest'],
            '.java': ['junit'],
            '.cpp': ['gtest'],
            '.c': ['unity'],
            '.go': ['testing'],
            '.rs': ['cargo test']
        }
    
    def generate_tests(self, file_path: str, test_type: str = 'unit', framework: str = None) -> Dict[str, Any]:
        """Generate tests for a given file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_extensions:
            return {"error": f"Unsupported file type: {ext}"}
        
        results = {
            "file_path": file_path,
            "test_type": test_type,
            "framework": framework,
            "generated_tests": [],
            "test_file_path": None,
            "coverage_info": {},
            "suggestions": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if ext == '.py':
                results.update(self._generate_python_tests(content, file_path, test_type, framework))
            elif ext in ['.js', '.ts']:
                results.update(self._generate_javascript_tests(content, file_path, test_type, framework))
            elif ext == '.java':
                results.update(self._generate_java_tests(content, file_path, test_type, framework))
            else:
                results["suggestions"].append(f"Test generation for {ext} files is not yet fully implemented")
            
            return results
            
        except Exception as e:
            return {"error": f"Failed to generate tests: {str(e)}"}
    
    def _generate_python_tests(self, content: str, file_path: str, test_type: str, framework: str) -> Dict[str, Any]:
        """Generate Python tests using pytest or unittest."""
        framework = framework or 'pytest'
        
        # Parse the Python file to extract functions and classes
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {str(e)}"}
        
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node))
                })
            elif isinstance(node, ast.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) and not child.name.startswith('_'):
                        methods.append({
                            "name": child.name,
                            "args": [arg.arg for arg in child.args.args],
                            "line": child.lineno,
                            "is_property": any(isinstance(d, ast.Name) and d.id == 'property' 
                                             for d in child.decorator_list)
                        })
                
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "docstring": ast.get_docstring(node)
                })
        
        # Generate test content
        test_content = self._create_python_test_content(functions, classes, file_path, framework)
        
        # Create test file path
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        test_dir = os.path.join(os.path.dirname(file_path), 'tests')
        os.makedirs(test_dir, exist_ok=True)
        test_file_path = os.path.join(test_dir, f"test_{base_name}.py")
        
        # Write test file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return {
            "generated_tests": functions + [{"name": f"{cls['name']} class", "methods": cls["methods"]} for cls in classes],
            "test_file_path": test_file_path,
            "framework": framework,
            "suggestions": [
                "Review generated tests and add specific assertions",
                "Consider edge cases and error conditions",
                "Add mock objects for external dependencies",
                "Implement integration tests if needed"
            ]
        }
    
    def _create_python_test_content(self, functions: List[Dict], classes: List[Dict], file_path: str, framework: str) -> str:
        """Create Python test file content."""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        relative_import = f"from ..{module_name} import *"
        
        if framework == 'pytest':
            content = f'''"""
Test file for {module_name}.py
Generated automatically by Jarvis AI Test Generator
"""
import pytest
{relative_import}


'''
            # Generate function tests
            for func in functions:
                content += f'''def test_{func["name"]}():
    """Test {func["name"]} function."""
    # TODO: Implement test logic
    # Example test structure:
    # result = {func["name"]}({", ".join(f"test_{arg}" for arg in func["args"])})
    # assert result == expected_value
    pass


'''
            
            # Generate class tests
            for cls in classes:
                content += f'''class Test{cls["name"]}:
    """Test class for {cls["name"]}."""
    
    @pytest.fixture
    def {cls["name"].lower()}_instance(self):
        """Create instance for testing."""
        return {cls["name"]}()
    
'''
                for method in cls["methods"]:
                    content += f'''    def test_{method["name"]}(self, {cls["name"].lower()}_instance):
        """Test {method["name"]} method."""
        # TODO: Implement test logic
        pass
    
'''
        
        else:  # unittest
            content = f'''"""
Test file for {module_name}.py
Generated automatically by Jarvis AI Test Generator
"""
import unittest
{relative_import}


'''
            for func in functions:
                content += f'''class Test{func["name"].title()}(unittest.TestCase):
    """Test {func["name"]} function."""
    
    def test_{func["name"]}_basic(self):
        """Basic test for {func["name"]}."""
        # TODO: Implement test logic
        pass


'''
            
            for cls in classes:
                content += f'''class Test{cls["name"]}(unittest.TestCase):
    """Test {cls["name"]} class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance = {cls["name"]}()
    
'''
                for method in cls["methods"]:
                    content += f'''    def test_{method["name"]}(self):
        """Test {method["name"]} method."""
        # TODO: Implement test logic
        pass
    
'''
            
            content += '''

if __name__ == '__main__':
    unittest.main()
'''
        
        return content
    
    def _generate_javascript_tests(self, content: str, file_path: str, test_type: str, framework: str) -> Dict[str, Any]:
        """Generate JavaScript/TypeScript tests."""
        framework = framework or 'jest'
        
        # Basic function extraction for JavaScript
        functions = self._extract_js_functions(content)
        
        # Create test file
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_path = os.path.join(os.path.dirname(file_path), f"{base_name}.test.js")
        
        test_content = self._create_javascript_test_content(functions, file_path, framework)
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return {
            "generated_tests": functions,
            "test_file_path": test_file_path,
            "framework": framework,
            "suggestions": [
                "Add mock implementations for external dependencies",
                "Consider async/await patterns in tests",
                "Add integration tests for complex workflows"
            ]
        }
    
    def _extract_js_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript functions from content."""
        functions = []
        
        # Regular expressions for different function patterns
        patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',  # function name()
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', # const name = () =>
            r'(\w+)\s*:\s*function\s*\([^)]*\)',  # name: function()
            r'(\w+)\s*\([^)]*\)\s*{',  # name() { (method style)
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                if func_name and not func_name.startswith('_'):
                    functions.append({
                        "name": func_name,
                        "line": content[:match.start()].count('\n') + 1
                    })
        
        return functions
    
    def _create_javascript_test_content(self, functions: List[Dict], file_path: str, framework: str) -> str:
        """Create JavaScript test file content."""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        content = f'''/**
 * Test file for {module_name}.js
 * Generated automatically by Jarvis AI Test Generator
 */

'''
        
        if framework == 'jest':
            content += f"const {{ {', '.join(f['name'] for f in functions)} }} = require('./{module_name}');\n\n"
            
            content += f"describe('{module_name}', () => {{\n"
            
            for func in functions:
                content += f'''
  describe('{func["name"]}', () => {{
    test('should work correctly', () => {{
      // TODO: Implement test logic
      // expect({func["name"]}()).toBe(expected);
    }});
    
    test('should handle edge cases', () => {{
      // TODO: Test edge cases
    }});
  }});
'''
            
            content += "});\n"
        
        return content
    
    def _generate_java_tests(self, content: str, file_path: str, test_type: str, framework: str) -> Dict[str, Any]:
        """Generate Java tests using JUnit."""
        framework = framework or 'junit'
        
        # Basic Java method extraction
        methods = self._extract_java_methods(content)
        class_name = self._extract_java_class_name(content)
        
        if not class_name:
            return {"error": "Could not find class name in Java file"}
        
        # Create test file
        test_class_name = f"{class_name}Test"
        test_file_path = os.path.join(os.path.dirname(file_path), f"{test_class_name}.java")
        
        test_content = self._create_java_test_content(methods, class_name, test_class_name)
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return {
            "generated_tests": methods,
            "test_file_path": test_file_path,
            "framework": framework,
            "suggestions": [
                "Add @BeforeEach and @AfterEach methods for setup/teardown",
                "Consider parameterized tests for multiple inputs",
                "Add integration tests for complex scenarios"
            ]
        }
    
    def _extract_java_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java methods from content."""
        methods = []
        
        # Pattern for Java methods
        pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\([^)]*\)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            method_name = match.group(3)
            if method_name and not method_name.startswith('_') and method_name not in ['main', 'equals', 'hashCode', 'toString']:
                methods.append({
                    "name": method_name,
                    "line": content[:match.start()].count('\n') + 1,
                    "visibility": match.group(1) or "package",
                    "is_static": bool(match.group(2))
                })
        
        return methods
    
    def _extract_java_class_name(self, content: str) -> str:
        """Extract Java class name from content."""
        pattern = r'public\s+class\s+(\w+)'
        match = re.search(pattern, content)
        return match.group(1) if match else None
    
    def _create_java_test_content(self, methods: List[Dict], class_name: str, test_class_name: str) -> str:
        """Create Java test file content."""
        content = f'''/**
 * Test class for {class_name}
 * Generated automatically by Jarvis AI Test Generator
 */

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

public class {test_class_name} {{
    
    private {class_name} instance;
    
    @BeforeEach
    public void setUp() {{
        instance = new {class_name}();
    }}
    
    @AfterEach
    public void tearDown() {{
        instance = null;
    }}

'''
        
        for method in methods:
            content += f'''
    @Test
    public void test{method["name"].title()}() {{
        // TODO: Implement test logic for {method["name"]}
        // Example:
        // Type result = instance.{method["name"]}();
        // assertEquals(expected, result);
    }}
'''
        
        content += "\n}\n"
        return content
    
    def analyze_coverage(self, file_path: str = None, test_file_path: str = None) -> Dict[str, Any]:
        """Analyze test coverage for the given file."""
        results = {
            "file_path": file_path,
            "test_file_path": test_file_path,
            "coverage_percentage": 0,
            "covered_lines": [],
            "uncovered_lines": [],
            "coverage_report": "",
            "suggestions": []
        }
        
        if not file_path:
            file_path = self.repository_path
        
        ext = os.path.splitext(file_path)[1].lower() if os.path.isfile(file_path) else '.py'
        
        try:
            if ext == '.py':
                return self._analyze_python_coverage(file_path, test_file_path)
            elif ext in ['.js', '.ts']:
                return self._analyze_javascript_coverage(file_path, test_file_path)
            elif ext == '.java':
                return self._analyze_java_coverage(file_path, test_file_path)
            else:
                results["suggestions"].append(f"Coverage analysis for {ext} files is not yet implemented")
                return results
                
        except Exception as e:
            results["error"] = f"Coverage analysis failed: {str(e)}"
            return results
    
    def _analyze_python_coverage(self, file_path: str, test_file_path: str = None) -> Dict[str, Any]:
        """Analyze Python test coverage using pytest-cov."""
        results = {
            "file_path": file_path,
            "test_file_path": test_file_path,
            "coverage_percentage": 0,
            "coverage_report": "",
            "suggestions": []
        }
        
        try:
            # Try to run coverage analysis
            if os.path.isfile(file_path):
                target = file_path
            else:
                target = file_path  # directory
            
            cmd = f"python -m coverage run --source={target} -m pytest {test_file_path or ''}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repository_path)
            
            if result.returncode == 0:
                # Get coverage report
                report_cmd = "python -m coverage report --show-missing"
                report_result = subprocess.run(report_cmd, shell=True, capture_output=True, text=True, cwd=self.repository_path)
                
                if report_result.returncode == 0:
                    results["coverage_report"] = report_result.stdout
                    
                    # Extract coverage percentage
                    lines = report_result.stdout.split('\n')
                    for line in lines:
                        if 'TOTAL' in line:
                            parts = line.split()
                            if len(parts) >= 4 and '%' in parts[-1]:
                                results["coverage_percentage"] = int(parts[-1].replace('%', ''))
                            break
                
                results["suggestions"] = [
                    "Run 'python -m coverage html' to generate detailed HTML report",
                    "Focus on testing uncovered lines and branches",
                    "Add tests for error handling and edge cases"
                ]
            else:
                results["error"] = f"Coverage analysis failed: {result.stderr}"
                results["suggestions"] = [
                    "Install coverage: pip install coverage pytest-cov",
                    "Ensure tests are runnable with pytest",
                    "Check file paths and test structure"
                ]
        
        except Exception as e:
            results["error"] = f"Coverage analysis error: {str(e)}"
        
        return results
    
    def _analyze_javascript_coverage(self, file_path: str, test_file_path: str = None) -> Dict[str, Any]:
        """Analyze JavaScript test coverage using Jest."""
        results = {
            "file_path": file_path,
            "test_file_path": test_file_path,
            "coverage_percentage": 0,
            "coverage_report": "",
            "suggestions": [
                "Run 'npm test -- --coverage' to generate coverage report",
                "Install Jest if not already available",
                "Configure jest.config.js for coverage settings"
            ]
        }
        
        return results
    
    def _analyze_java_coverage(self, file_path: str, test_file_path: str = None) -> Dict[str, Any]:
        """Analyze Java test coverage using JaCoCo."""
        results = {
            "file_path": file_path,
            "test_file_path": test_file_path,
            "coverage_percentage": 0,
            "coverage_report": "",
            "suggestions": [
                "Configure JaCoCo in build.gradle or pom.xml",
                "Run tests with coverage: 'mvn test jacoco:report'",
                "Check target/site/jacoco/index.html for detailed report"
            ]
        }
        
        return results
    
    def suggest_test_improvements(self, test_file_path: str) -> Dict[str, Any]:
        """Analyze existing tests and suggest improvements."""
        if not os.path.exists(test_file_path):
            return {"error": f"Test file not found: {test_file_path}"}
        
        results = {
            "test_file_path": test_file_path,
            "analysis": {},
            "suggestions": [],
            "quality_score": 0
        }
        
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ext = os.path.splitext(test_file_path)[1].lower()
            
            if ext == '.py':
                results.update(self._analyze_python_test_quality(content))
            elif ext in ['.js', '.ts']:
                results.update(self._analyze_javascript_test_quality(content))
            
            return results
            
        except Exception as e:
            return {"error": f"Test analysis failed: {str(e)}"}
    
    def _analyze_python_test_quality(self, content: str) -> Dict[str, Any]:
        """Analyze Python test quality."""
        analysis = {
            "test_count": len(re.findall(r'def test_\w+', content)),
            "has_fixtures": 'fixture' in content,
            "has_mocks": any(mock in content for mock in ['mock', 'patch', 'MagicMock']),
            "has_parametrize": 'parametrize' in content,
            "has_docstrings": '"""' in content or "'''" in content,
            "assertion_count": len(re.findall(r'assert\s+', content))
        }
        
        suggestions = []
        quality_score = 0
        
        if analysis["test_count"] > 0:
            quality_score += 20
        else:
            suggestions.append("Add more test functions")
        
        if analysis["has_fixtures"]:
            quality_score += 15
        else:
            suggestions.append("Consider using pytest fixtures for test setup")
        
        if analysis["has_mocks"]:
            quality_score += 15
        else:
            suggestions.append("Add mock objects for external dependencies")
        
        if analysis["has_parametrize"]:
            quality_score += 20
        else:
            suggestions.append("Use @pytest.mark.parametrize for testing multiple inputs")
        
        if analysis["has_docstrings"]:
            quality_score += 10
        else:
            suggestions.append("Add docstrings to test functions")
        
        if analysis["assertion_count"] >= analysis["test_count"]:
            quality_score += 20
        else:
            suggestions.append("Ensure each test has proper assertions")
        
        return {
            "analysis": analysis,
            "suggestions": suggestions,
            "quality_score": min(quality_score, 100)
        }
    
    def _analyze_javascript_test_quality(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript test quality."""
        analysis = {
            "test_count": len(re.findall(r'test\(|it\(', content)),
            "describe_blocks": len(re.findall(r'describe\(', content)),
            "has_mocks": any(mock in content for mock in ['jest.mock', 'jest.fn', 'sinon']),
            "has_async_tests": 'async' in content,
            "expectation_count": len(re.findall(r'expect\(', content))
        }
        
        suggestions = []
        quality_score = 0
        
        if analysis["test_count"] > 0:
            quality_score += 25
        
        if analysis["describe_blocks"] > 0:
            quality_score += 15
        else:
            suggestions.append("Organize tests with describe blocks")
        
        if analysis["has_mocks"]:
            quality_score += 20
        else:
            suggestions.append("Consider using Jest mocks for dependencies")
        
        if analysis["expectation_count"] >= analysis["test_count"]:
            quality_score += 40
        else:
            suggestions.append("Ensure each test has proper expectations")
        
        return {
            "analysis": analysis,
            "suggestions": suggestions,
            "quality_score": min(quality_score, 100)
        }


def generate_tests_for_file(file_path: str, test_type: str = 'unit', framework: str = None) -> Dict[str, Any]:
    """Generate tests for a specific file."""
    generator = TestGenerator()
    return generator.generate_tests(file_path, test_type, framework)


def analyze_test_coverage(file_path: str = None, test_file_path: str = None) -> Dict[str, Any]:
    """Analyze test coverage for a file or directory."""
    generator = TestGenerator()
    return generator.analyze_coverage(file_path, test_file_path)


def suggest_test_improvements(test_file_path: str) -> Dict[str, Any]:
    """Suggest improvements for existing tests."""
    generator = TestGenerator()
    return generator.suggest_test_improvements(test_file_path)


def test_generator_handler(action: str, **kwargs) -> Dict[str, Any]:
    """Handle test generation requests."""
    generator = TestGenerator(kwargs.get('repository_path'))
    
    if action == 'generate':
        return generator.generate_tests(
            kwargs.get('file_path'),
            kwargs.get('test_type', 'unit'),
            kwargs.get('framework')
        )
    elif action == 'coverage':
        return generator.analyze_coverage(
            kwargs.get('file_path'),
            kwargs.get('test_file_path')
        )
    elif action == 'improve':
        return generator.suggest_test_improvements(kwargs.get('test_file_path'))
    else:
        return {"error": f"Unknown action: {action}"}