"""
Documentation Generation Module
Provides automated documentation generation from code, comments, and repository structure.
"""
import os
import ast
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess


class DocumentationGenerator:
    def __init__(self, repository_path: str = None):
        self.repository_path = repository_path or os.getcwd()
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.md'}
        self.doc_formats = ['markdown', 'rst', 'html', 'json']
    
    def generate_documentation(self, target_path: str, doc_format: str = 'markdown', 
                             include_private: bool = False, output_dir: str = None) -> Dict[str, Any]:
        """Generate comprehensive documentation for code files or directories."""
        if not os.path.exists(target_path):
            return {"error": f"Path not found: {target_path}"}
        
        output_dir = output_dir or os.path.join(self.repository_path, 'docs')
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            "target_path": target_path,
            "doc_format": doc_format,
            "output_dir": output_dir,
            "generated_files": [],
            "summary": {
                "total_files": 0,
                "documented_functions": 0,
                "documented_classes": 0,
                "missing_docstrings": []
            },
            "suggestions": []
        }
        
        try:
            if os.path.isfile(target_path):
                self._document_file(target_path, output_dir, doc_format, include_private, results)
            else:
                self._document_directory(target_path, output_dir, doc_format, include_private, results)
            
            # Generate index file
            self._generate_index(output_dir, doc_format, results)
            
            return results
            
        except Exception as e:
            return {"error": f"Documentation generation failed: {str(e)}"}
    
    def _document_file(self, file_path: str, output_dir: str, doc_format: str, 
                      include_private: bool, results: Dict[str, Any]) -> None:
        """Generate documentation for a single file."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_extensions:
            results["suggestions"].append(f"Skipping unsupported file type: {ext}")
            return
        
        results["summary"]["total_files"] += 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if ext == '.py':
            doc_data = self._extract_python_documentation(content, file_path, include_private)
        elif ext in ['.js', '.ts']:
            doc_data = self._extract_javascript_documentation(content, file_path, include_private)
        elif ext == '.java':
            doc_data = self._extract_java_documentation(content, file_path, include_private)
        elif ext in ['.cpp', '.c', '.h', '.hpp']:
            doc_data = self._extract_cpp_documentation(content, file_path, include_private)
        elif ext == '.go':
            doc_data = self._extract_go_documentation(content, file_path, include_private)
        elif ext == '.rs':
            doc_data = self._extract_rust_documentation(content, file_path, include_private)
        elif ext == '.md':
            doc_data = self._extract_markdown_content(content, file_path)
        else:
            doc_data = {"functions": [], "classes": [], "description": ""}
        
        # Update summary
        results["summary"]["documented_functions"] += len(doc_data.get("functions", []))
        results["summary"]["documented_classes"] += len(doc_data.get("classes", []))
        results["summary"]["missing_docstrings"].extend(doc_data.get("missing_docstrings", []))
        
        # Generate documentation file
        doc_filename = self._generate_doc_file(file_path, doc_data, output_dir, doc_format)
        results["generated_files"].append(doc_filename)
    
    def _document_directory(self, dir_path: str, output_dir: str, doc_format: str,
                           include_private: bool, results: Dict[str, Any]) -> None:
        """Generate documentation for all files in a directory."""
        for root, dirs, files in os.walk(dir_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_path = os.path.join(root, file)
                self._document_file(file_path, output_dir, doc_format, include_private, results)
    
    def _extract_python_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from Python files."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"functions": [], "classes": [], "description": "Syntax error in file"}
        
        doc_data = {
            "file_path": file_path,
            "description": ast.get_docstring(tree) or "",
            "functions": [],
            "classes": [],
            "imports": [],
            "missing_docstrings": []
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    doc_data["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    doc_data["imports"].append(f"{module}.{alias.name}" if module else alias.name)
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not include_private and node.name.startswith('_'):
                    continue
                
                func_doc = {
                    "name": node.name,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node) or "",
                    "args": [],
                    "returns": None,
                    "decorators": []
                }
                
                # Extract arguments
                for arg in node.args.args:
                    func_doc["args"].append({
                        "name": arg.arg,
                        "annotation": ast.unparse(arg.annotation) if arg.annotation else None
                    })
                
                # Extract return annotation
                if node.returns:
                    func_doc["returns"] = ast.unparse(node.returns)
                
                # Extract decorators
                for decorator in node.decorator_list:
                    func_doc["decorators"].append(ast.unparse(decorator))
                
                if not func_doc["docstring"]:
                    doc_data["missing_docstrings"].append(f"Function: {node.name} (line {node.lineno})")
                
                doc_data["functions"].append(func_doc)
            
            elif isinstance(node, ast.ClassDef):
                if not include_private and node.name.startswith('_'):
                    continue
                
                class_doc = {
                    "name": node.name,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node) or "",
                    "methods": [],
                    "bases": [],
                    "decorators": []
                }
                
                # Extract base classes
                for base in node.bases:
                    class_doc["bases"].append(ast.unparse(base))
                
                # Extract decorators
                for decorator in node.decorator_list:
                    class_doc["decorators"].append(ast.unparse(decorator))
                
                # Extract methods
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        if not include_private and child.name.startswith('_') and child.name != '__init__':
                            continue
                        
                        method_doc = {
                            "name": child.name,
                            "line": child.lineno,
                            "docstring": ast.get_docstring(child) or "",
                            "args": [],
                            "returns": None,
                            "is_static": any(isinstance(d, ast.Name) and d.id == 'staticmethod' 
                                           for d in child.decorator_list),
                            "is_class_method": any(isinstance(d, ast.Name) and d.id == 'classmethod' 
                                                 for d in child.decorator_list),
                            "is_property": any(isinstance(d, ast.Name) and d.id == 'property' 
                                             for d in child.decorator_list)
                        }
                        
                        # Extract method arguments (skip 'self' for instance methods)
                        start_idx = 0 if method_doc["is_static"] else 1
                        for arg in child.args.args[start_idx:]:
                            method_doc["args"].append({
                                "name": arg.arg,
                                "annotation": ast.unparse(arg.annotation) if arg.annotation else None
                            })
                        
                        if child.returns:
                            method_doc["returns"] = ast.unparse(child.returns)
                        
                        if not method_doc["docstring"]:
                            doc_data["missing_docstrings"].append(
                                f"Method: {node.name}.{child.name} (line {child.lineno})")
                        
                        class_doc["methods"].append(method_doc)
                
                if not class_doc["docstring"]:
                    doc_data["missing_docstrings"].append(f"Class: {node.name} (line {node.lineno})")
                
                doc_data["classes"].append(class_doc)
        
        return doc_data
    
    def _extract_javascript_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from JavaScript/TypeScript files."""
        doc_data = {
            "file_path": file_path,
            "description": "",
            "functions": [],
            "classes": [],
            "exports": [],
            "missing_docstrings": []
        }
        
        lines = content.split('\n')
        
        # Extract file description from top comments
        for i, line in enumerate(lines[:10]):
            if line.strip().startswith('/**') or line.strip().startswith('/*'):
                desc_lines = []
                for j in range(i, min(i + 20, len(lines))):
                    if '*/' in lines[j]:
                        break
                    desc_lines.append(lines[j].strip())
                doc_data["description"] = '\n'.join(desc_lines)
                break
        
        # Extract functions
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{',
            r'async\s+function\s+(\w+)\s*\([^)]*\)\s*{'
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                if not include_private and func_name.startswith('_'):
                    continue
                
                line_num = content[:match.start()].count('\n') + 1
                
                # Look for JSDoc comment before function
                func_lines = content[:match.start()].split('\n')
                docstring = self._extract_jsdoc(func_lines)
                
                if not docstring:
                    doc_data["missing_docstrings"].append(f"Function: {func_name} (line {line_num})")
                
                doc_data["functions"].append({
                    "name": func_name,
                    "line": line_num,
                    "docstring": docstring,
                    "is_async": 'async' in match.group(0)
                })
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            if not include_private and class_name.startswith('_'):
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            # Look for JSDoc comment before class
            class_lines = content[:match.start()].split('\n')
            docstring = self._extract_jsdoc(class_lines)
            
            if not docstring:
                doc_data["missing_docstrings"].append(f"Class: {class_name} (line {line_num})")
            
            doc_data["classes"].append({
                "name": class_name,
                "line": line_num,
                "docstring": docstring,
                "extends": match.group(2)
            })
        
        return doc_data
    
    def _extract_jsdoc(self, lines: List[str]) -> str:
        """Extract JSDoc comment from lines."""
        doc_lines = []
        in_doc = False
        
        for line in reversed(lines[-10:]):  # Look at last 10 lines
            stripped = line.strip()
            if stripped.endswith('*/'):
                in_doc = True
                doc_lines.append(stripped)
            elif in_doc:
                doc_lines.append(stripped)
                if stripped.startswith('/**'):
                    break
            elif stripped and not stripped.startswith('//'):
                break
        
        if doc_lines:
            doc_lines.reverse()
            return '\n'.join(doc_lines)
        return ""
    
    def _extract_java_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from Java files."""
        doc_data = {
            "file_path": file_path,
            "description": "",
            "functions": [],
            "classes": [],
            "missing_docstrings": []
        }
        
        # Extract package and imports
        package_match = re.search(r'package\s+([\w.]+);', content)
        if package_match:
            doc_data["package"] = package_match.group(1)
        
        # Extract class documentation
        class_pattern = r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Look for Javadoc before class
            class_lines = content[:match.start()].split('\n')
            docstring = self._extract_javadoc(class_lines)
            
            if not docstring:
                doc_data["missing_docstrings"].append(f"Class: {class_name} (line {line_num})")
            
            class_doc = {
                "name": class_name,
                "line": line_num,
                "docstring": docstring,
                "extends": match.group(2),
                "implements": match.group(3).split(',') if match.group(3) else []
            }
            
            doc_data["classes"].append(class_doc)
        
        # Extract method documentation
        method_pattern = r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*{'
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            method_name = match.group(3)
            if not include_private and match.group(1) == 'private':
                continue
            if method_name in ['equals', 'hashCode', 'toString', 'main']:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            # Look for Javadoc before method
            method_lines = content[:match.start()].split('\n')
            docstring = self._extract_javadoc(method_lines)
            
            if not docstring:
                doc_data["missing_docstrings"].append(f"Method: {method_name} (line {line_num})")
            
            doc_data["functions"].append({
                "name": method_name,
                "line": line_num,
                "docstring": docstring,
                "visibility": match.group(1) or "package",
                "is_static": bool(match.group(2))
            })
        
        return doc_data
    
    def _extract_javadoc(self, lines: List[str]) -> str:
        """Extract Javadoc comment from lines."""
        doc_lines = []
        in_doc = False
        
        for line in reversed(lines[-10:]):
            stripped = line.strip()
            if stripped.endswith('*/'):
                in_doc = True
                doc_lines.append(stripped)
            elif in_doc:
                doc_lines.append(stripped)
                if stripped.startswith('/**'):
                    break
            elif stripped and not stripped.startswith('//'):
                break
        
        if doc_lines:
            doc_lines.reverse()
            return '\n'.join(doc_lines)
        return ""
    
    def _extract_cpp_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from C++ files."""
        doc_data = {
            "file_path": file_path,
            "description": "",
            "functions": [],
            "classes": [],
            "missing_docstrings": []
        }
        
        # Extract function declarations
        function_pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*[{;]'
        matches = re.finditer(function_pattern, content)
        
        for match in matches:
            return_type = match.group(1)
            func_name = match.group(2)
            
            if func_name in ['if', 'for', 'while', 'switch']:  # Skip keywords
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            doc_data["functions"].append({
                "name": func_name,
                "line": line_num,
                "return_type": return_type,
                "docstring": ""  # C++ doc extraction would need more sophisticated parsing
            })
        
        return doc_data
    
    def _extract_go_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from Go files."""
        doc_data = {
            "file_path": file_path,
            "description": "",
            "functions": [],
            "structs": [],
            "missing_docstrings": []
        }
        
        # Extract functions
        function_pattern = r'func\s+(\w+)\s*\([^)]*\)(?:\s*\([^)]*\))?\s*{'
        matches = re.finditer(function_pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            if not include_private and func_name[0].islower():
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            doc_data["functions"].append({
                "name": func_name,
                "line": line_num,
                "docstring": "",
                "is_exported": func_name[0].isupper()
            })
        
        return doc_data
    
    def _extract_rust_documentation(self, content: str, file_path: str, include_private: bool) -> Dict[str, Any]:
        """Extract documentation from Rust files."""
        doc_data = {
            "file_path": file_path,
            "description": "",
            "functions": [],
            "structs": [],
            "missing_docstrings": []
        }
        
        # Extract functions
        function_pattern = r'(?:pub\s+)?fn\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^{]+)?\s*{'
        matches = re.finditer(function_pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            is_public = 'pub' in match.group(0)
            
            if not include_private and not is_public:
                continue
            
            doc_data["functions"].append({
                "name": func_name,
                "line": line_num,
                "docstring": "",
                "is_public": is_public
            })
        
        return doc_data
    
    def _extract_markdown_content(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract content from Markdown files."""
        return {
            "file_path": file_path,
            "description": content[:500] + "..." if len(content) > 500 else content,
            "headers": re.findall(r'^#+\s+(.+)$', content, re.MULTILINE),
            "functions": [],
            "classes": []
        }
    
    def _generate_doc_file(self, file_path: str, doc_data: Dict[str, Any], 
                          output_dir: str, doc_format: str) -> str:
        """Generate documentation file in specified format."""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        if doc_format == 'markdown':
            return self._generate_markdown_doc(base_name, doc_data, output_dir)
        elif doc_format == 'rst':
            return self._generate_rst_doc(base_name, doc_data, output_dir)
        elif doc_format == 'html':
            return self._generate_html_doc(base_name, doc_data, output_dir)
        elif doc_format == 'json':
            return self._generate_json_doc(base_name, doc_data, output_dir)
        else:
            raise ValueError(f"Unsupported documentation format: {doc_format}")
    
    def _generate_markdown_doc(self, base_name: str, doc_data: Dict[str, Any], output_dir: str) -> str:
        """Generate Markdown documentation."""
        output_file = os.path.join(output_dir, f"{base_name}.md")
        
        content = f"""# {base_name}

**File:** {doc_data.get('file_path', '')}

## Description

{doc_data.get('description', 'No description available.')}

"""
        
        # Add imports if available
        if 'imports' in doc_data and doc_data['imports']:
            content += "## Imports\n\n"
            for imp in doc_data['imports']:
                content += f"- `{imp}`\n"
            content += "\n"
        
        # Add classes
        if doc_data.get('classes'):
            content += "## Classes\n\n"
            for cls in doc_data['classes']:
                content += f"### {cls['name']}\n\n"
                if cls.get('docstring'):
                    content += f"{cls['docstring']}\n\n"
                
                if cls.get('bases'):
                    content += f"**Inherits from:** {', '.join(cls['bases'])}\n\n"
                
                if cls.get('methods'):
                    content += "#### Methods\n\n"
                    for method in cls['methods']:
                        content += f"##### {method['name']}\n\n"
                        if method.get('docstring'):
                            content += f"{method['docstring']}\n\n"
                        
                        if method.get('args'):
                            content += "**Parameters:**\n"
                            for arg in method['args']:
                                annotation = f": {arg['annotation']}" if arg.get('annotation') else ""
                                content += f"- `{arg['name']}{annotation}`\n"
                            content += "\n"
                        
                        if method.get('returns'):
                            content += f"**Returns:** `{method['returns']}`\n\n"
        
        # Add functions
        if doc_data.get('functions'):
            content += "## Functions\n\n"
            for func in doc_data['functions']:
                content += f"### {func['name']}\n\n"
                if func.get('docstring'):
                    content += f"{func['docstring']}\n\n"
                
                if func.get('args'):
                    content += "**Parameters:**\n"
                    for arg in func['args']:
                        annotation = f": {arg['annotation']}" if arg.get('annotation') else ""
                        content += f"- `{arg['name']}{annotation}`\n"
                    content += "\n"
                
                if func.get('returns'):
                    content += f"**Returns:** `{func['returns']}`\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def _generate_rst_doc(self, base_name: str, doc_data: Dict[str, Any], output_dir: str) -> str:
        """Generate reStructuredText documentation."""
        output_file = os.path.join(output_dir, f"{base_name}.rst")
        
        title = base_name
        content = f"""{title}
{'=' * len(title)}

**File:** {doc_data.get('file_path', '')}

Description
-----------

{doc_data.get('description', 'No description available.')}

"""
        
        if doc_data.get('classes'):
            content += "Classes\n-------\n\n"
            for cls in doc_data['classes']:
                content += f"{cls['name']}\n{'~' * len(cls['name'])}\n\n"
                if cls.get('docstring'):
                    content += f"{cls['docstring']}\n\n"
        
        if doc_data.get('functions'):
            content += "Functions\n---------\n\n"
            for func in doc_data['functions']:
                content += f"{func['name']}\n{'~' * len(func['name'])}\n\n"
                if func.get('docstring'):
                    content += f"{func['docstring']}\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def _generate_html_doc(self, base_name: str, doc_data: Dict[str, Any], output_dir: str) -> str:
        """Generate HTML documentation."""
        output_file = os.path.join(output_dir, f"{base_name}.html")
        
        content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{base_name} Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ color: #333; border-bottom: 2px solid #333; }}
        .section {{ margin: 20px 0; }}
        .code {{ background-color: #f4f4f4; padding: 2px 4px; font-family: monospace; }}
        .docstring {{ background-color: #f9f9f9; padding: 10px; border-left: 4px solid #ccc; }}
    </style>
</head>
<body>
    <h1 class="header">{base_name}</h1>
    <p><strong>File:</strong> <span class="code">{doc_data.get('file_path', '')}</span></p>
    
    <div class="section">
        <h2>Description</h2>
        <div class="docstring">{doc_data.get('description', 'No description available.')}</div>
    </div>
"""
        
        if doc_data.get('classes'):
            content += '<div class="section"><h2>Classes</h2>'
            for cls in doc_data['classes']:
                content += f'<h3>{cls["name"]}</h3>'
                if cls.get('docstring'):
                    content += f'<div class="docstring">{cls["docstring"]}</div>'
            content += '</div>'
        
        if doc_data.get('functions'):
            content += '<div class="section"><h2>Functions</h2>'
            for func in doc_data['functions']:
                content += f'<h3>{func["name"]}</h3>'
                if func.get('docstring'):
                    content += f'<div class="docstring">{func["docstring"]}</div>'
            content += '</div>'
        
        content += """
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def _generate_json_doc(self, base_name: str, doc_data: Dict[str, Any], output_dir: str) -> str:
        """Generate JSON documentation."""
        output_file = os.path.join(output_dir, f"{base_name}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def _generate_index(self, output_dir: str, doc_format: str, results: Dict[str, Any]) -> None:
        """Generate index file for all documentation."""
        if doc_format == 'markdown':
            index_file = os.path.join(output_dir, 'README.md')
            content = "# Documentation Index\n\nGenerated by Jarvis AI Documentation Generator\n\n## Files\n\n"
            for file_path in results["generated_files"]:
                filename = os.path.basename(file_path)
                content += f"- [{filename}]({filename})\n"
        elif doc_format == 'html':
            index_file = os.path.join(output_dir, 'index.html')
            content = """<!DOCTYPE html>
<html>
<head><title>Documentation Index</title></head>
<body>
<h1>Documentation Index</h1>
<p>Generated by Jarvis AI Documentation Generator</p>
<h2>Files</h2>
<ul>
"""
            for file_path in results["generated_files"]:
                filename = os.path.basename(file_path)
                content += f'<li><a href="{filename}">{filename}</a></li>\n'
            content += "</ul></body></html>"
        else:
            return  # Skip index for other formats
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_api_documentation(self, module_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Generate API documentation using automated tools."""
        output_dir = output_dir or os.path.join(self.repository_path, 'api_docs')
        
        results = {
            "module_path": module_path,
            "output_dir": output_dir,
            "generated": False,
            "tool_used": None,
            "error": None
        }
        
        try:
            ext = os.path.splitext(module_path)[1].lower()
            
            if ext == '.py':
                # Try to use Sphinx for Python
                results.update(self._generate_sphinx_docs(module_path, output_dir))
            elif ext in ['.js', '.ts']:
                # Try to use JSDoc for JavaScript
                results.update(self._generate_jsdoc_docs(module_path, output_dir))
            elif ext == '.java':
                # Try to use Javadoc for Java
                results.update(self._generate_javadoc_docs(module_path, output_dir))
            else:
                results["error"] = f"API documentation not supported for {ext} files"
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            return results
    
    def _generate_sphinx_docs(self, module_path: str, output_dir: str) -> Dict[str, Any]:
        """Generate Sphinx documentation for Python modules."""
        try:
            # Create sphinx configuration
            os.makedirs(output_dir, exist_ok=True)
            
            # Basic conf.py
            conf_content = '''
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'API Documentation'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon']
html_theme = 'alabaster'
'''
            
            with open(os.path.join(output_dir, 'conf.py'), 'w') as f:
                f.write(conf_content)
            
            # Try to run sphinx-apidoc
            cmd = f"sphinx-apidoc -o {output_dir} {os.path.dirname(module_path)}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Try to build HTML
                build_cmd = f"sphinx-build -b html {output_dir} {output_dir}/_build"
                build_result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
                
                return {
                    "generated": build_result.returncode == 0,
                    "tool_used": "Sphinx",
                    "output": build_result.stdout if build_result.returncode == 0 else build_result.stderr
                }
            else:
                return {
                    "generated": False,
                    "tool_used": "Sphinx",
                    "error": "Sphinx not available or failed to run"
                }
                
        except Exception as e:
            return {"generated": False, "tool_used": "Sphinx", "error": str(e)}
    
    def _generate_jsdoc_docs(self, module_path: str, output_dir: str) -> Dict[str, Any]:
        """Generate JSDoc documentation for JavaScript modules."""
        try:
            cmd = f"jsdoc {module_path} -d {output_dir}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "generated": result.returncode == 0,
                "tool_used": "JSDoc",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {"generated": False, "tool_used": "JSDoc", "error": str(e)}
    
    def _generate_javadoc_docs(self, module_path: str, output_dir: str) -> Dict[str, Any]:
        """Generate Javadoc documentation for Java modules."""
        try:
            cmd = f"javadoc -d {output_dir} {module_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                "generated": result.returncode == 0,
                "tool_used": "Javadoc",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {"generated": False, "tool_used": "Javadoc", "error": str(e)}


def generate_documentation(target_path: str, doc_format: str = 'markdown', 
                         include_private: bool = False, output_dir: str = None) -> Dict[str, Any]:
    """Generate documentation for a file or directory."""
    generator = DocumentationGenerator()
    return generator.generate_documentation(target_path, doc_format, include_private, output_dir)


def generate_api_docs(module_path: str, output_dir: str = None) -> Dict[str, Any]:
    """Generate API documentation using automated tools."""
    generator = DocumentationGenerator()
    return generator.generate_api_documentation(module_path, output_dir)


def documentation_handler(action: str, **kwargs) -> Dict[str, Any]:
    """Handle documentation generation requests."""
    generator = DocumentationGenerator(kwargs.get('repository_path'))
    
    if action == 'generate':
        return generator.generate_documentation(
            kwargs.get('target_path'),
            kwargs.get('doc_format', 'markdown'),
            kwargs.get('include_private', False),
            kwargs.get('output_dir')
        )
    elif action == 'api_docs':
        return generator.generate_api_documentation(
            kwargs.get('module_path'),
            kwargs.get('output_dir')
        )
    else:
        return {"error": f"Unknown action: {action}"}