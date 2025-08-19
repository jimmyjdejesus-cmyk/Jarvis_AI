"""
Code Search Module
Provides semantic and lexical code search capabilities across repositories.
Supports various search types: function names, class names, variables, patterns, etc.
"""
import os
import re
import ast
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import difflib


@dataclass
class SearchResult:
    """Represents a single search result."""
    file_path: str
    line_number: int
    content: str
    context_before: List[str]
    context_after: List[str]
    match_type: str
    confidence: float
    

class CodeSearcher:
    def __init__(self, repository_path: str = None):
        self.repository_path = repository_path or os.getcwd()
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', 
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala'
        }
        self.index = {}
        self._build_index()
    
    def _build_index(self):
        """Build search index for faster lookups."""
        self.index = {
            'functions': {},
            'classes': {},
            'variables': {},
            'imports': {},
            'files': []
        }
        
        for root, dirs, files in os.walk(self.repository_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.supported_extensions:
                    self.index['files'].append(file_path)
                    if ext == '.py':
                        self._index_python_file(file_path)
    
    def _index_python_file(self, file_path: str):
        """Index Python file for functions, classes, and variables."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            class IndexVisitor(ast.NodeVisitor):
                def __init__(self, file_path):
                    self.file_path = file_path
                    self.functions = []
                    self.classes = []
                    self.variables = []
                    self.imports = []
                
                def visit_FunctionDef(self, node):
                    self.functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'file': self.file_path,
                        'args': [arg.arg for arg in node.args.args] if hasattr(node.args, 'args') else []
                    })
                    self.generic_visit(node)
                
                def visit_ClassDef(self, node):
                    self.classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'file': self.file_path,
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                    })
                    self.generic_visit(node)
                
                def visit_Assign(self, node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.variables.append({
                                'name': target.id,
                                'line': node.lineno,
                                'file': self.file_path
                            })
                    self.generic_visit(node)
                
                def visit_Import(self, node):
                    for alias in node.names:
                        self.imports.append({
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno,
                            'file': self.file_path,
                            'type': 'import'
                        })
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    for alias in node.names:
                        self.imports.append({
                            'name': alias.name,
                            'alias': alias.asname,
                            'module': node.module,
                            'line': node.lineno,
                            'file': self.file_path,
                            'type': 'from_import'
                        })
                    self.generic_visit(node)
            
            visitor = IndexVisitor(file_path)
            visitor.visit(tree)
            
            # Add to index
            for func in visitor.functions:
                if func['name'] not in self.index['functions']:
                    self.index['functions'][func['name']] = []
                self.index['functions'][func['name']].append(func)
            
            for cls in visitor.classes:
                if cls['name'] not in self.index['classes']:
                    self.index['classes'][cls['name']] = []
                self.index['classes'][cls['name']].append(cls)
            
            for var in visitor.variables:
                if var['name'] not in self.index['variables']:
                    self.index['variables'][var['name']] = []
                self.index['variables'][var['name']].append(var)
            
            for imp in visitor.imports:
                if imp['name'] not in self.index['imports']:
                    self.index['imports'][imp['name']] = []
                self.index['imports'][imp['name']].append(imp)
                
        except (SyntaxError, UnicodeDecodeError):
            pass  # Skip files with syntax errors or encoding issues
    
    def search(self, query: str, search_type: str = 'all', 
               case_sensitive: bool = False, regex: bool = False,
               context_lines: int = 3) -> List[SearchResult]:
        """
        Search for code patterns.
        
        Args:
            query: Search query
            search_type: Type of search ('all', 'function', 'class', 'variable', 'text', 'semantic')
            case_sensitive: Whether search should be case sensitive
            regex: Whether query is a regular expression
            context_lines: Number of context lines to include
        
        Returns:
            List of SearchResult objects
        """
        results = []
        
        if search_type in ['all', 'function']:
            results.extend(self._search_functions(query, case_sensitive, regex, context_lines))
        
        if search_type in ['all', 'class']:
            results.extend(self._search_classes(query, case_sensitive, regex, context_lines))
        
        if search_type in ['all', 'variable']:
            results.extend(self._search_variables(query, case_sensitive, regex, context_lines))
        
        if search_type in ['all', 'text']:
            results.extend(self._search_text(query, case_sensitive, regex, context_lines))
        
        if search_type == 'semantic':
            results.extend(self._semantic_search(query, context_lines))
        
        # Sort by confidence score
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        return results
    
    def _search_functions(self, query: str, case_sensitive: bool, 
                         regex: bool, context_lines: int) -> List[SearchResult]:
        """Search for function definitions."""
        results = []
        
        for func_name, func_list in self.index['functions'].items():
            if self._matches_query(func_name, query, case_sensitive, regex):
                for func_info in func_list:
                    result = self._create_search_result(
                        func_info['file'], func_info['line'], 
                        f"def {func_name}({', '.join(func_info['args'])})",
                        'function', context_lines, 1.0
                    )
                    if result:
                        results.append(result)
        
        return results
    
    def _search_classes(self, query: str, case_sensitive: bool,
                       regex: bool, context_lines: int) -> List[SearchResult]:
        """Search for class definitions."""
        results = []
        
        for class_name, class_list in self.index['classes'].items():
            if self._matches_query(class_name, query, case_sensitive, regex):
                for class_info in class_list:
                    bases_str = f"({', '.join(class_info['bases'])})" if class_info['bases'] else ""
                    result = self._create_search_result(
                        class_info['file'], class_info['line'],
                        f"class {class_name}{bases_str}",
                        'class', context_lines, 1.0
                    )
                    if result:
                        results.append(result)
        
        return results
    
    def _search_variables(self, query: str, case_sensitive: bool,
                         regex: bool, context_lines: int) -> List[SearchResult]:
        """Search for variable assignments."""
        results = []
        
        for var_name, var_list in self.index['variables'].items():
            if self._matches_query(var_name, query, case_sensitive, regex):
                for var_info in var_list:
                    result = self._create_search_result(
                        var_info['file'], var_info['line'],
                        f"{var_name} = ...",
                        'variable', context_lines, 0.8
                    )
                    if result:
                        results.append(result)
        
        return results
    
    def _search_text(self, query: str, case_sensitive: bool,
                    regex: bool, context_lines: int) -> List[SearchResult]:
        """Search for text patterns in all files."""
        results = []
        
        for file_path in self.index['files']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if self._matches_query(line, query, case_sensitive, regex):
                        result = self._create_search_result(
                            file_path, i + 1, line.strip(),
                            'text', context_lines, 0.6
                        )
                        if result:
                            results.append(result)
                            
            except (UnicodeDecodeError, IOError):
                continue
        
        return results
    
    def _semantic_search(self, query: str, context_lines: int) -> List[SearchResult]:
        """Perform semantic search based on code similarity."""
        results = []
        
        # Simple semantic search based on similarity of function/class names
        # and their context
        query_words = set(re.findall(r'\w+', query.lower()))
        
        # Search functions semantically
        for func_name, func_list in self.index['functions'].items():
            func_words = set(re.findall(r'\w+', func_name.lower()))
            similarity = self._calculate_similarity(query_words, func_words)
            
            if similarity > 0.3:  # Threshold for semantic similarity
                for func_info in func_list:
                    result = self._create_search_result(
                        func_info['file'], func_info['line'],
                        f"def {func_name}({', '.join(func_info['args'])})",
                        'semantic_function', context_lines, similarity
                    )
                    if result:
                        results.append(result)
        
        # Search classes semantically
        for class_name, class_list in self.index['classes'].items():
            class_words = set(re.findall(r'\w+', class_name.lower()))
            similarity = self._calculate_similarity(query_words, class_words)
            
            if similarity > 0.3:
                for class_info in class_list:
                    result = self._create_search_result(
                        class_info['file'], class_info['line'],
                        f"class {class_name}",
                        'semantic_class', context_lines, similarity
                    )
                    if result:
                        results.append(result)
        
        return results
    
    def _matches_query(self, text: str, query: str, case_sensitive: bool, regex: bool) -> bool:
        """Check if text matches the query."""
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return bool(re.search(query, text, flags))
            except re.error:
                return False
        else:
            if not case_sensitive:
                text = text.lower()
                query = query.lower()
            return query in text
    
    def _calculate_similarity(self, words1: set, words2: set) -> float:
        """Calculate similarity between two sets of words."""
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _create_search_result(self, file_path: str, line_number: int, 
                             content: str, match_type: str, 
                             context_lines: int, confidence: float) -> Optional[SearchResult]:
        """Create a SearchResult object with context."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get context lines
            start_idx = max(0, line_number - context_lines - 1)
            end_idx = min(len(lines), line_number + context_lines)
            
            context_before = [line.rstrip() for line in lines[start_idx:line_number-1]]
            context_after = [line.rstrip() for line in lines[line_number:end_idx]]
            
            # If content is not provided, get it from the file
            if not content.strip():
                content = lines[line_number - 1].rstrip() if line_number <= len(lines) else ""
            
            return SearchResult(
                file_path=file_path,
                line_number=line_number,
                content=content,
                context_before=context_before,
                context_after=context_after,
                match_type=match_type,
                confidence=confidence
            )
            
        except (IOError, IndexError):
            return None
    
    def find_similar_functions(self, function_name: str, threshold: float = 0.5) -> List[SearchResult]:
        """Find functions with similar names."""
        results = []
        
        for func_name, func_list in self.index['functions'].items():
            similarity = difflib.SequenceMatcher(None, function_name.lower(), func_name.lower()).ratio()
            
            if similarity >= threshold and func_name != function_name:
                for func_info in func_list:
                    result = self._create_search_result(
                        func_info['file'], func_info['line'],
                        f"def {func_name}({', '.join(func_info['args'])})",
                        'similar_function', 3, similarity
                    )
                    if result:
                        results.append(result)
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def find_function_usage(self, function_name: str) -> List[SearchResult]:
        """Find where a function is called."""
        results = []
        
        # Search for function calls in all files
        for file_path in self.index['files']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    # Look for function calls (basic pattern)
                    if re.search(rf'\b{re.escape(function_name)}\s*\(', line):
                        result = self._create_search_result(
                            file_path, i + 1, line.strip(),
                            'function_usage', 3, 0.8
                        )
                        if result:
                            results.append(result)
                            
            except (UnicodeDecodeError, IOError):
                continue
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search index statistics."""
        return {
            'total_files': len(self.index['files']),
            'total_functions': sum(len(func_list) for func_list in self.index['functions'].values()),
            'total_classes': sum(len(class_list) for class_list in self.index['classes'].values()),
            'total_variables': sum(len(var_list) for var_list in self.index['variables'].values()),
            'total_imports': sum(len(imp_list) for imp_list in self.index['imports'].values()),
            'indexed_extensions': list(self.supported_extensions)
        }


def search_code(query: str, repository_path: str = None, search_type: str = 'all',
               case_sensitive: bool = False, regex: bool = False,
               context_lines: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function for code search.
    
    Args:
        query: Search query
        repository_path: Path to repository (defaults to current directory)
        search_type: Type of search
        case_sensitive: Case sensitive search
        regex: Treat query as regex
        context_lines: Number of context lines
    
    Returns:
        List of search results as dictionaries
    """
    searcher = CodeSearcher(repository_path)
    results = searcher.search(query, search_type, case_sensitive, regex, context_lines)
    
    return [
        {
            'file_path': result.file_path,
            'line_number': result.line_number,
            'content': result.content,
            'context_before': result.context_before,
            'context_after': result.context_after,
            'match_type': result.match_type,
            'confidence': result.confidence
        }
        for result in results
    ]


def find_definition(symbol: str, repository_path: str = None) -> List[Dict[str, Any]]:
    """
    Find the definition of a symbol (function, class, variable).
    
    Args:
        symbol: Symbol name to find
        repository_path: Repository path
    
    Returns:
        List of definitions found
    """
    searcher = CodeSearcher(repository_path)
    results = []
    
    # Search in functions
    if symbol in searcher.index['functions']:
        for func_info in searcher.index['functions'][symbol]:
            results.append({
                'type': 'function',
                'name': symbol,
                'file': func_info['file'],
                'line': func_info['line'],
                'args': func_info['args']
            })
    
    # Search in classes
    if symbol in searcher.index['classes']:
        for class_info in searcher.index['classes'][symbol]:
            results.append({
                'type': 'class',
                'name': symbol,
                'file': class_info['file'],
                'line': class_info['line'],
                'bases': class_info['bases']
            })
    
    # Search in variables
    if symbol in searcher.index['variables']:
        for var_info in searcher.index['variables'][symbol]:
            results.append({
                'type': 'variable',
                'name': symbol,
                'file': var_info['file'],
                'line': var_info['line']
            })
    
    return results