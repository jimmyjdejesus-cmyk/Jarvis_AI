"""
Code Intelligence Engine
Provides GitHub Copilot-like code completion using local Ollama models.

Key Features:
- Code context extraction and analysis
- Project-wide imports, classes, and functions scanning  
- AST-based code understanding
- Human feedback collection and application
- Automatic prioritization of successful completions
"""

import ast
import os
import re
import json
import sqlite3
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import requests

# Import existing modules (optional for standalone operation)
try:
    # Try relative imports first (when used as module)
    try:
        from . import tools
    except ImportError:
        tools = None
    try:
        from . import repo_context
    except ImportError:
        repo_context = None
except ImportError:
    # Fall back to absolute imports (when used directly)
    try:
        import tools
    except ImportError:
        tools = None
    try:
        import repo_context
    except ImportError:
        repo_context = None


@dataclass
class CodeContext:
    """Container for code context information."""
    file_path: str
    cursor_line: int
    cursor_column: int
    current_function: Optional[str] = None
    current_class: Optional[str] = None
    imports: List[str] = None
    local_variables: List[str] = None
    surrounding_code: str = ""
    project_symbols: Dict[str, Any] = None


@dataclass
class CodeCompletion:
    """Container for code completion results."""
    suggestion: str
    confidence: float
    context_relevance: float
    completion_type: str  # 'line', 'function', 'class', 'import'
    metadata: Dict[str, Any] = None


class CodeIntelligenceEngine:
    """Main code intelligence engine providing Copilot-like functionality."""
    
    def __init__(self, db_path: str = "janus_database.db"):
        self.db_path = db_path
        self.ollama_endpoint = "http://localhost:11434"
        self.supported_languages = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs'}
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables for code intelligence."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Code completion feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_completion_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                file_path TEXT NOT NULL,
                cursor_position TEXT NOT NULL,
                context_hash TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                accepted BOOLEAN NOT NULL,
                completion_type TEXT NOT NULL,
                confidence_score REAL,
                model_used TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feedback_notes TEXT
            )
        ''')
        
        # Code completion analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_completion_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session_id TEXT,
                file_path TEXT NOT NULL,
                language TEXT,
                completion_type TEXT NOT NULL,
                context_size INTEGER,
                generation_time_ms INTEGER,
                model_used TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Successful patterns cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS successful_code_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE NOT NULL,
                pattern_context TEXT NOT NULL,
                completion_text TEXT NOT NULL,
                success_count INTEGER DEFAULT 1,
                language TEXT NOT NULL,
                completion_type TEXT NOT NULL,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_code_context(self, file_path: str, cursor_line: int, cursor_column: int = 0) -> CodeContext:
        """
        Extract comprehensive code context for intelligent completion.
        
        Args:
            file_path: Path to the source file
            cursor_line: Line number where cursor is positioned (1-based)
            cursor_column: Column number where cursor is positioned (0-based)
            
        Returns:
            CodeContext object with extracted information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Basic context
        context = CodeContext(
            file_path=file_path,
            cursor_line=cursor_line,
            cursor_column=cursor_column
        )
        
        # Get surrounding code (5 lines before and after)
        start_line = max(0, cursor_line - 6)
        end_line = min(len(lines), cursor_line + 5)
        context.surrounding_code = '\n'.join(lines[start_line:end_line])
        
        # Language-specific analysis
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            self._extract_python_context(content, cursor_line, context)
        elif file_ext in ['.js', '.ts']:
            self._extract_javascript_context(content, cursor_line, context)
        else:
            # Generic context extraction
            self._extract_generic_context(content, cursor_line, context)
        
        # Get project-wide symbols
        context.project_symbols = self._get_project_symbols(file_path)
        
        return context
    
    def _extract_python_context(self, content: str, cursor_line: int, context: CodeContext):
        """Extract Python-specific context using AST analysis."""
        try:
            tree = ast.parse(content)
            
            # Find imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            context.imports = imports
            
            # Find current function/class context
            current_func = None
            current_class = None
            local_vars = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'lineno') and node.lineno <= cursor_line:
                        # Check if cursor is within this function
                        func_end = self._get_node_end_line(node)
                        if cursor_line <= func_end:
                            current_func = node.name
                            # Extract function parameters as local variables
                            for arg in node.args.args:
                                local_vars.append(arg.arg)
                
                elif isinstance(node, ast.ClassDef):
                    if hasattr(node, 'lineno') and node.lineno <= cursor_line:
                        class_end = self._get_node_end_line(node)
                        if cursor_line <= class_end:
                            current_class = node.name
                
                elif isinstance(node, ast.Assign):
                    # Extract variable assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            local_vars.append(target.id)
            
            context.current_function = current_func
            context.current_class = current_class
            context.local_variables = list(set(local_vars))
            
        except SyntaxError:
            # Fallback for invalid Python syntax
            self._extract_generic_context(content, cursor_line, context)
    
    def _extract_javascript_context(self, content: str, cursor_line: int, context: CodeContext):
        """Extract JavaScript/TypeScript context using regex patterns."""
        lines = content.split('\n')
        
        # Find imports/requires
        imports = []
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*\s+=\s+require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for line in lines[:cursor_line]:
            for pattern in import_patterns:
                matches = re.findall(pattern, line)
                imports.extend(matches)
        
        context.imports = imports
        
        # Find current function context
        current_func = None
        for i in range(cursor_line - 1, -1, -1):
            line = lines[i]
            func_match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=|\w+\s*:\s*function|(\w+)\s*\(.*\)\s*=>', line)
            if func_match:
                current_func = func_match.group(1) or func_match.group(2) or func_match.group(3)
                break
        
        context.current_function = current_func
        
        # Find local variables (simplified)
        local_vars = []
        for i in range(max(0, cursor_line - 20), cursor_line):
            line = lines[i]
            var_matches = re.findall(r'(?:var|let|const)\s+(\w+)', line)
            local_vars.extend(var_matches)
        
        context.local_variables = list(set(local_vars))
    
    def _extract_generic_context(self, content: str, cursor_line: int, context: CodeContext):
        """Generic context extraction for unsupported languages."""
        lines = content.split('\n')
        
        # Extract basic patterns
        local_vars = []
        for i in range(max(0, cursor_line - 10), cursor_line):
            if i < len(lines):
                line = lines[i]
                # Simple variable detection
                var_matches = re.findall(r'\b([a-zA-Z_]\w*)\s*=', line)
                local_vars.extend(var_matches)
        
        context.local_variables = list(set(local_vars))
    
    def _get_node_end_line(self, node: ast.AST) -> int:
        """Get the ending line number of an AST node."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        
        # Fallback: find the maximum line number of all child nodes
        max_line = getattr(node, 'lineno', 0)
        for child in ast.walk(node):
            if hasattr(child, 'lineno') and child.lineno:
                max_line = max(max_line, child.lineno)
        
        return max_line
    
    def _get_project_symbols(self, file_path: str) -> Dict[str, Any]:
        """Get project-wide symbols using existing repo_context module."""
        if repo_context is None:
            return {}
            
        try:
            project_root = self._find_project_root(file_path)
            if project_root:
                context = repo_context.get_repository_context(project_root)
                return context.get('code_patterns', {})
        except Exception as e:
            print(f"Warning: Could not extract project symbols: {e}")
        
        return {}
    
    def _find_project_root(self, file_path: str) -> Optional[str]:
        """Find the root directory of the project."""
        current_dir = os.path.dirname(os.path.abspath(file_path))
        
        # Look for common project indicators
        indicators = ['.git', 'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml']
        
        while current_dir != os.path.dirname(current_dir):  # Not root
            for indicator in indicators:
                if os.path.exists(os.path.join(current_dir, indicator)):
                    return current_dir
            current_dir = os.path.dirname(current_dir)
        
        return None
    
    def generate_code_completion(
        self, 
        context: CodeContext, 
        model: str = "llama3.2",
        max_suggestions: int = 3
    ) -> List[CodeCompletion]:
        """
        Generate intelligent code completions using Ollama.
        
        Args:
            context: Code context information
            model: Ollama model to use
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            List of CodeCompletion objects
        """
        start_time = time.time()
        
        try:
            # Build context-aware prompt
            prompt = self._build_completion_prompt(context)
            
            # Check for cached successful patterns first
            cached_suggestions = self._get_cached_suggestions(context)
            
            # Generate new suggestions using Ollama
            new_suggestions = self._generate_ollama_completions(prompt, model, max_suggestions)
            
            # Combine and rank suggestions
            all_suggestions = cached_suggestions + new_suggestions
            ranked_suggestions = self._rank_suggestions(all_suggestions, context)
            
            # Log analytics
            self._log_completion_analytics(
                context, 
                model, 
                len(ranked_suggestions), 
                int((time.time() - start_time) * 1000),
                success=True
            )
            
            return ranked_suggestions[:max_suggestions]
            
        except Exception as e:
            # Log error analytics
            self._log_completion_analytics(
                context, 
                model, 
                0, 
                int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e)
            )
            
            return []
    
    def _build_completion_prompt(self, context: CodeContext) -> str:
        """Build a context-aware prompt for code completion."""
        file_ext = Path(context.file_path).suffix.lower()
        language = self._get_language_name(file_ext)
        
        prompt_parts = [
            f"You are an expert {language} code completion assistant.",
            f"File: {os.path.basename(context.file_path)}",
            f"Language: {language}",
        ]
        
        if context.current_class:
            prompt_parts.append(f"Current class: {context.current_class}")
        
        if context.current_function:
            prompt_parts.append(f"Current function: {context.current_function}")
        
        if context.imports:
            prompt_parts.append(f"Available imports: {', '.join(context.imports[:10])}")
        
        if context.local_variables:
            prompt_parts.append(f"Local variables: {', '.join(context.local_variables[:10])}")
        
        prompt_parts.extend([
            "",
            "Code context:",
            "```" + language.lower(),
            context.surrounding_code,
            "```",
            "",
            f"Generate {language} code completion suggestions for line {context.cursor_line}.",
            "Provide 1-3 contextually relevant completions.",
            "Each completion should be on a separate line, prefixed with '###COMPLETION:'",
            "Consider the existing code style, patterns, and context.",
            "Only suggest syntactically correct and semantically meaningful code."
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_language_name(self, file_ext: str) -> str:
        """Get language name from file extension."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C',
            '.hpp': 'C++',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        return language_map.get(file_ext, 'Unknown')
    
    def _generate_ollama_completions(self, prompt: str, model: str, max_suggestions: int) -> List[CodeCompletion]:
        """Generate completions using Ollama API."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more focused completions
                "top_p": 0.9,
                "max_tokens": 200
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                response_text = data.get("response", "").strip()
                
                # Parse completions from response
                completions = []
                for line in response_text.split('\n'):
                    if line.startswith('###COMPLETION:'):
                        completion_text = line.replace('###COMPLETION:', '').strip()
                        if completion_text:
                            completions.append(CodeCompletion(
                                suggestion=completion_text,
                                confidence=0.7,  # Default confidence
                                context_relevance=0.8,
                                completion_type='line',
                                metadata={'model': model, 'generated': True}
                            ))
                
                return completions[:max_suggestions]
            
        except Exception as e:
            print(f"Error generating Ollama completions: {e}")
        
        return []
    
    def _get_cached_suggestions(self, context: CodeContext) -> List[CodeCompletion]:
        """Get cached successful completion patterns."""
        # For now, return empty list - can be enhanced later
        return []
    
    def _rank_suggestions(self, suggestions: List[CodeCompletion], context: CodeContext) -> List[CodeCompletion]:
        """Rank suggestions based on relevance and historical success."""
        # Simple ranking for now - can be enhanced with ML models
        return sorted(suggestions, key=lambda x: (x.confidence + x.context_relevance) / 2, reverse=True)
    
    def record_feedback(
        self, 
        context: CodeContext, 
        suggestion: str, 
        accepted: bool,
        completion_type: str = 'line',
        username: str = 'anonymous',
        notes: str = None
    ):
        """Record user feedback on code completions."""
        context_hash = self._hash_context(context)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO code_completion_feedback 
            (username, file_path, cursor_position, context_hash, suggestion, 
             accepted, completion_type, feedback_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            context.file_path,
            f"{context.cursor_line}:{context.cursor_column}",
            context_hash,
            suggestion,
            accepted,
            completion_type,
            notes
        ))
        
        # Update successful patterns cache if accepted
        if accepted:
            self._update_successful_pattern(context, suggestion, completion_type)
        
        conn.commit()
        conn.close()
    
    def _hash_context(self, context: CodeContext) -> str:
        """Generate a hash for the code context."""
        import hashlib
        
        context_str = f"{context.file_path}:{context.cursor_line}:{context.surrounding_code}"
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _update_successful_pattern(self, context: CodeContext, suggestion: str, completion_type: str):
        """Update successful patterns cache."""
        pattern_hash = self._hash_context(context)
        file_ext = Path(context.file_path).suffix.lower()
        language = self._get_language_name(file_ext)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute(
            'SELECT id, success_count FROM successful_code_patterns WHERE pattern_hash = ?',
            (pattern_hash,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing pattern
            cursor.execute(
                'UPDATE successful_code_patterns SET success_count = success_count + 1, last_used = ? WHERE id = ?',
                (datetime.now(), result[0])
            )
        else:
            # Insert new pattern
            cursor.execute('''
                INSERT INTO successful_code_patterns 
                (pattern_hash, pattern_context, completion_text, language, completion_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                pattern_hash,
                context.surrounding_code,
                suggestion,
                language,
                completion_type
            ))
        
        conn.commit()
        conn.close()
    
    def _log_completion_analytics(
        self, 
        context: CodeContext, 
        model: str, 
        suggestion_count: int,
        generation_time_ms: int,
        success: bool,
        username: str = 'anonymous',
        session_id: str = None,
        error_message: str = None
    ):
        """Log completion analytics."""
        file_ext = Path(context.file_path).suffix.lower()
        language = self._get_language_name(file_ext)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO code_completion_analytics 
            (username, session_id, file_path, language, completion_type, 
             context_size, generation_time_ms, model_used, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            session_id,
            context.file_path,
            language,
            'line',  # Default completion type
            len(context.surrounding_code),
            generation_time_ms,
            model,
            success,
            error_message
        ))
        
        conn.commit()
        conn.close()
    
    def get_completion_analytics(self, username: str = None) -> Dict[str, Any]:
        """Get code completion analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Base query
        base_where = "WHERE 1=1"
        params = []
        
        if username:
            base_where += " AND username = ?"
            params.append(username)
        
        # Total completions
        cursor.execute(f"SELECT COUNT(*) FROM code_completion_analytics {base_where}", params)
        total_completions = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute(f"SELECT AVG(success) FROM code_completion_analytics {base_where}", params)
        success_rate = cursor.fetchone()[0] or 0
        
        # Average generation time
        cursor.execute(f"SELECT AVG(generation_time_ms) FROM code_completion_analytics {base_where}", params)
        avg_generation_time = cursor.fetchone()[0] or 0
        
        # Language distribution
        cursor.execute(f"SELECT language, COUNT(*) FROM code_completion_analytics {base_where} GROUP BY language", params)
        language_stats = dict(cursor.fetchall())
        
        # Feedback stats
        cursor.execute(f"SELECT AVG(accepted) FROM code_completion_feedback {base_where}", params)
        acceptance_rate = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_completions": total_completions,
            "success_rate": round(success_rate * 100, 2),
            "acceptance_rate": round(acceptance_rate * 100, 2),
            "avg_generation_time_ms": round(avg_generation_time, 2),
            "language_distribution": language_stats
        }


# Convenience functions for integration
def get_code_completion(
    file_path: str, 
    cursor_line: int, 
    cursor_column: int = 0,
    model: str = "llama3.2",
    username: str = 'anonymous'
) -> List[Dict[str, Any]]:
    """
    Convenience function to get code completion suggestions.
    
    Returns:
        List of completion dictionaries for easy UI integration
    """
    engine = CodeIntelligenceEngine()
    
    try:
        context = engine.extract_code_context(file_path, cursor_line, cursor_column)
        completions = engine.generate_code_completion(context, model)
        
        return [
            {
                'suggestion': comp.suggestion,
                'confidence': comp.confidence,
                'type': comp.completion_type,
                'metadata': comp.metadata
            }
            for comp in completions
        ]
    except Exception as e:
        return [{'error': str(e)}]


def record_completion_feedback(
    file_path: str,
    cursor_line: int,
    cursor_column: int,
    suggestion: str,
    accepted: bool,
    username: str = 'anonymous'
) -> bool:
    """
    Convenience function to record completion feedback.
    
    Returns:
        True if feedback was recorded successfully
    """
    engine = CodeIntelligenceEngine()
    
    try:
        context = engine.extract_code_context(file_path, cursor_line, cursor_column)
        engine.record_feedback(context, suggestion, accepted, username=username)
        return True
    except Exception as e:
        print(f"Error recording feedback: {e}")
        return False