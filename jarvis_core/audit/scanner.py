# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/




Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

"""
Base scanner classes for the AdaptiveMind AI audit system.

This module provides the foundation for all scanning operations including
security vulnerability detection, code quality analysis, and dependency scanning.
"""

import os
import ast
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

from .models import AuditFinding, ScanConfiguration, AuditCategory, SeverityLevel


class BaseScanner(ABC):
    """
    Abstract base class for all audit scanners.
    
    Provides common functionality for file analysis and finding generation.
    """
    
    def __init__(self, config: ScanConfiguration):
        """
        Initialize the scanner with configuration.
        
        Args:
            config: Scan configuration settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def scan_files(self, file_paths: List[Path]) -> List[AuditFinding]:
        """
        Scan files and return findings.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            List of audit findings
        """
        pass
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string, or None if reading fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Could not read {file_path}: {e}")
            return None
    
    def _create_finding(
        self,
        category: AuditCategory,
        severity: SeverityLevel,
        title: str,
        description: str,
        file_path: Path,
        line_number: Optional[int] = None,
        remediation: str = "",
        cwe_id: Optional[str] = None,
        cvss_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditFinding:
        """
        Create a standardized audit finding.
        
        Args:
            category: Category of the finding
            severity: Severity level
            title: Brief description
            description: Detailed description
            file_path: File location
            line_number: Specific line (if applicable)
            remediation: Fix recommendations
            cwe_id: CWE identifier (if security related)
            cvss_score: CVSS score (if applicable)
            metadata: Additional metadata
            
        Returns:
            Configured AuditFinding instance
        """
        return AuditFinding(
            id=f"{category.value}_{hash(f'{file_path}:{line_number}:{title}')}",
            category=category,
            severity=severity,
            title=title,
            description=description,
            file_path=str(file_path),
            line_number=line_number,
            remediation=remediation,
            cwe_id=cwe_id,
            cvss_score=cvss_score,
            metadata=metadata or {}
        )


class SecurityScanner(BaseScanner):
    """
    Security vulnerability scanner using bandit and other security tools.
    
    Detects common security vulnerabilities in Python code including:
    - SQL injection patterns
    - Command injection
    - Insecure random number generation
    - Hardcoded secrets
    - Insecure file operations
    """
    
    def scan_files(self, file_paths: List[Path]) -> List[AuditFinding]:
        """
        Scan files for security vulnerabilities.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Try to run bandit if available
        bandit_findings = self._run_bandit_scan(file_paths)
        findings.extend(bandit_findings)
        
        # Static security pattern analysis
        for file_path in file_paths:
            content = self._read_file_content(file_path)
            if content:
                findings.extend(self._scan_security_patterns(file_path, content))
        
        return findings
    
    def _run_bandit_scan(self, file_paths: List[Path]) -> List[AuditFinding]:
        """
        Run bandit security scanner.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            List of bandit findings converted to AuditFindings
        """
        findings = []
        
        try:
            # Create temporary directory with files to scan
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy files to temp directory
                for file_path in file_paths:
                    if file_path.exists():
                        dest_path = temp_path / file_path.name
                        dest_path.write_text(file_path.read_text())
                
                # Run bandit
                result = subprocess.run(
                    ["bandit", "-r", str(temp_path), "-f", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    import json
                    bandit_results = json.loads(result.stdout)
                    
                    for issue in bandit_results.get("results", []):
                        finding = self._convert_bandit_finding(issue)
                        if finding:
                            findings.append(finding)
                            
        except subprocess.TimeoutExpired:
            self.logger.warning("Bandit scan timed out")
        except Exception as e:
            self.logger.debug(f"Bandit scan failed: {e}")
        
        return findings
    
    def _convert_bandit_finding(self, issue: Dict[str, Any]) -> Optional[AuditFinding]:
        """
        Convert bandit finding to AuditFinding.
        
        Args:
            issue: Bandit issue dictionary
            
        Returns:
            Converted AuditFinding or None
        """
        try:
            # Map bandit severity to our severity levels
            severity_map = {
                "HIGH": SeverityLevel.HIGH,
                "MEDIUM": SeverityLevel.MEDIUM,
                "LOW": SeverityLevel.LOW
            }
            
            severity = severity_map.get(issue.get("issue_severity", "MEDIUM"), SeverityLevel.MEDIUM)
            
            # Get CWE ID if available
            cwe_id = None
            if "cwe" in issue:
                cwe_id = f"CWE-{issue['cwe']}"
            
            # Calculate CVSS score
            cvss_score = None
            if severity == SeverityLevel.HIGH:
                cvss_score = 7.5
            elif severity == SeverityLevel.MEDIUM:
                cvss_score = 5.0
            elif severity == SeverityLevel.LOW:
                cvss_score = 2.5
            
            return self._create_finding(
                category=AuditCategory.SECURITY,
                severity=severity,
                title=issue.get("issue_text", "Security issue detected"),
                description=issue.get("issue_text", ""),
                file_path=Path(issue.get("filename", "unknown")),
                line_number=issue.get("line_number"),
                remediation="Review and fix security vulnerability according to bandit recommendations",
                cwe_id=cwe_id,
                cvss_score=cvss_score,
                metadata={
                    "tool": "bandit",
                    "test_id": issue.get("test_id"),
                    "confidence": issue.get("issue_confidence")
                }
            )
        except Exception as e:
            self.logger.debug(f"Failed to convert bandit finding: {e}")
            return None
    
    def _scan_security_patterns(self, file_path: Path, content: str) -> List[AuditFinding]:
        """
        Scan for security patterns using regex patterns.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Security patterns to detect
        patterns = {
            "hardcoded_secrets": {
                "pattern": r"(?i)(password|secret|key|token)\s*=\s*['\"][^'\"]{10,}['\"]",
                "severity": SeverityLevel.HIGH,
                "title": "Hardcoded Secret Detected",
                "description": "Potential hardcoded secret or password found in source code",
                "remediation": "Move secrets to environment variables or secure configuration",
                "cwe_id": "CWE-798"
            },
            "sql_injection": {
                "pattern": r"(?i)(execute|query)\s*\(\s*['\"].*%.*['\"]",
                "severity": SeverityLevel.HIGH,
                "title": "Potential SQL Injection",
                "description": "SQL query construction using string formatting may be vulnerable to injection",
                "remediation": "Use parameterized queries or ORM methods",
                "cwe_id": "CWE-89"
            },
            "eval_usage": {
                "pattern": r"\beval\s*\(",
                "severity": SeverityLevel.HIGH,
                "title": "Use of eval() Function",
                "description": "Use of eval() function can lead to code injection vulnerabilities",
                "remediation": "Avoid eval() or use ast.literal_eval() for safe evaluation",
                "cwe_id": "CWE-94"
            },
            "subprocess_shell": {
                "pattern": r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
                "severity": SeverityLevel.MEDIUM,
                "title": "Insecure subprocess call",
                "description": "Use of shell=True in subprocess can be vulnerable to injection",
                "remediation": "Avoid shell=True or properly validate and sanitize inputs",
                "cwe_id": "CWE-78"
            }
        }
        
        lines = content.split('\n')
        
        for pattern_name, pattern_config in patterns.items():
            try:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern_config["pattern"], line):
                        finding = self._create_finding(
                            category=AuditCategory.SECURITY,
                            severity=pattern_config["severity"],
                            title=pattern_config["title"],
                            description=pattern_config["description"],
                            file_path=file_path,
                            line_number=line_num,
                            remediation=pattern_config["remediation"],
                            cwe_id=pattern_config["cwe_id"],
                            cvss_score=7.5 if pattern_config["severity"] == SeverityLevel.HIGH else 5.0,
                            metadata={"pattern_type": pattern_name}
                        )
                        findings.append(finding)
            except re.error as e:
                self.logger.debug(f"Invalid regex pattern {pattern_name}: {e}")
        
        return findings


class CodeQualityScanner(BaseScanner):
    """
    Code quality scanner using various static analysis tools.
    
    Analyzes code for:
    - Code complexity
    - Style violations
    - Maintainability issues
    - Potential bugs
    """
    
    def scan_files(self, file_paths: List[Path]) -> List[AuditFinding]:
        """
        Scan files for code quality issues.
        
        Args:
            file_paths: List of file paths to scan
            
        Returns:
            List of code quality findings
        """
        findings = []
        
        # Scan each file for quality issues
        for file_path in file_paths:
            content = self._read_file_content(file_path)
            if content:
                findings.extend(self._analyze_file_quality(file_path, content))
        
        return findings
    
    def _analyze_file_quality(self, file_path: Path, content: str) -> List[AuditFinding]:
        """
        Analyze a single file for quality issues.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of quality findings
        """
        findings = []
        lines = content.split('\n')
        
        # Check for overly long lines
        long_lines = [(i+1, line) for i, line in enumerate(lines) if len(line) > 120]
        for line_num, line in long_lines:
            finding = self._create_finding(
                category=AuditCategory.CODE_QUALITY,
                severity=SeverityLevel.LOW,
                title="Line too long",
                description=f"Line exceeds 120 characters (length: {len(line)})",
                file_path=file_path,
                line_number=line_num,
                remediation="Break long lines into multiple lines for better readability",
                metadata={"line_length": len(line)}
            )
            findings.append(finding)
        
        # Check for high cyclomatic complexity
        complexity = self._calculate_complexity(content)
        if complexity > 10:
            finding = self._create_finding(
                category=AuditCategory.CODE_QUALITY,
                severity=SeverityLevel.MEDIUM if complexity > 15 else SeverityLevel.LOW,
                title="High cyclomatic complexity",
                description=f"Cyclomatic complexity of {complexity} exceeds recommended threshold of 10",
                file_path=file_path,
                remediation="Refactor complex functions into smaller, more manageable pieces",
                metadata={"complexity": complexity}
            )
            findings.append(finding)
        
        # Check for TODO/FIXME comments
        todo_pattern = r"#\s*(TODO|FIXME|XXX|HACK)"
        for line_num, line in enumerate(lines, 1):
            if re.search(todo_pattern, line, re.IGNORECASE):
                finding = self._create_finding(
                    category=AuditCategory.CODE_QUALITY,
                    severity=SeverityLevel.INFO,
                    title="Technical debt marker",
                    description=f"Found '{line.strip()}' comment indicating technical debt",
                    file_path=file_path,
                    line_number=line_num,
                    remediation="Address the TODO/FIXME item or remove the comment if no longer needed",
                    metadata={"comment_type": "technical_debt"}
                )
                findings.append(finding)
        
        # Check for magic numbers
        magic_numbers = self._find_magic_numbers(content)
        for line_num, numbers in magic_numbers.items():
            finding = self._create_finding(
                category=AuditCategory.CODE_QUALITY,
                severity=SeverityLevel.LOW,
                title="Magic numbers in code",
                description=f"Found magic numbers: {numbers} on line {line_num}",
                file_path=file_path,
                line_number=line_num,
                remediation="Replace magic numbers with named constants for better maintainability",
                metadata={"magic_numbers": numbers}
            )
            findings.append(finding)
        
        return findings
    
    def _calculate_complexity(self, content: str) -> int:
        """
        Calculate cyclomatic complexity of the code.
        
        Args:
            content: Source code content
            
        Returns:
            Cyclomatic complexity score
        """
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                # Count decision points
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, ast.comprehension):
                    complexity += 1
                    
            return complexity
        except Exception:
            return 1
    
    def _find_magic_numbers(self, content: str) -> Dict[int, List[int]]:
        """
        Find magic numbers in the code.
        
        Args:
            content: Source code content
            
        Returns:
            Dictionary mapping line numbers to lists of magic numbers
        """
        magic_numbers = {}
        lines = content.split('\n')
        
        # Common numbers that are not considered magic
        allowed_numbers = {0, 1, -1, 2}
        
        for line_num, line in enumerate(lines, 1):
            # Find numbers in the line
            numbers = re.findall(r'\b\d+\b', line)
            magic_nums = []
            
            for num_str in numbers:
                try:
                    num = int(num_str)
                    if num not in allowed_numbers and num > 9:  # Consider > 9 as potentially magic
                        magic_nums.append(num)
                except ValueError:
                    continue
            
            if magic_nums:
                magic_numbers[line_num] = magic_nums
        
        return magic_numbers


class DependencyScanner(BaseScanner):
    """
    Dependency vulnerability scanner.
    
    Scans for known vulnerabilities in project dependencies.
    """
    
    def scan_files(self, file_paths: List[Path]) -> List[AuditFinding]:
        """
        Scan for dependency vulnerabilities.
        
        Args:
            file_paths: List of file paths (used to find dependency files)
            
        Returns:
            List of dependency vulnerability findings
        """
        findings = []
        
        # Try to run safety if available
        safety_findings = self._run_safety_scan()
        findings.extend(safety_findings)
        
        # Check for outdated dependencies in requirements files
        for file_path in file_paths:
            if file_path.name in ["requirements.txt", "pyproject.toml", "Pipfile"]:
                content = self._read_file_content(file_path)
                if content:
                    findings.extend(self._scan_dependency_file(file_path, content))
        
        return findings
    
    def _run_safety_scan(self) -> List[AuditFinding]:
        """
        Run safety scanner for dependency vulnerabilities.
        
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                import json
                safety_results = json.loads(result.stdout)
                
                for vuln in safety_results:
                    finding = self._convert_safety_finding(vuln)
                    if finding:
                        findings.append(finding)
                        
        except subprocess.TimeoutExpired:
            self.logger.warning("Safety scan timed out")
        except Exception as e:
            self.logger.debug(f"Safety scan failed: {e}")
        
        return findings
    
    def _convert_safety_finding(self, vuln: Dict[str, Any]) -> Optional[AuditFinding]:
        """
        Convert safety finding to AuditFinding.
        
        Args:
            vuln: Safety vulnerability dictionary
            
        Returns:
            Converted AuditFinding or None
        """
        try:
            # Determine severity based on CVE information
            severity = SeverityLevel.MEDIUM
            if "advisory" in vuln:
                advisory = vuln["advisory"]
                if "severity" in advisory:
                    sev = advisory["severity"].lower()
                    if sev in ["high", "critical"]:
                        severity = SeverityLevel.HIGH
                    elif sev == "low":
                        severity = SeverityLevel.LOW
            
            return self._create_finding(
                category=AuditCategory.DEPENDENCY,
                severity=severity,
                title=f"Vulnerable dependency: {vuln.get('package_name', 'unknown')}",
                description=vuln.get("advisory", {}).get("description", "Security vulnerability in dependency"),
                file_path=Path("requirements.txt"),  # Generic location
                remediation="Update the vulnerable dependency to the latest secure version",
                metadata={
                    "tool": "safety",
                    "package_name": vuln.get("package_name"),
                    "installed_version": vuln.get("installed_version"),
                    "vulnerable_versions": vuln.get("vulnerable_versions")
                }
            )
        except Exception as e:
            self.logger.debug(f"Failed to convert safety finding: {e}")
            return None
    
    def _scan_dependency_file(self, file_path: Path, content: str) -> List[AuditFinding]:
        """
        Scan dependency file for issues.
        
        Args:
            file_path: Path to the dependency file
            content: File content
            
        Returns:
            List of dependency findings
        """
        findings = []
        
        if file_path.name == "requirements.txt":
            # Check for unpinned versions
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check if version is pinned
                    if '==' not in line and '>=' not in line and '~=' not in line:
                        finding = self._create_finding(
                            category=AuditCategory.DEPENDENCY,
                            severity=SeverityLevel.LOW,
                            title="Unpinned dependency version",
                            description=f"Dependency '{line}' does not specify a version constraint",
                            file_path=file_path,
                            line_number=line_num,
                            remediation="Pin dependency versions to ensure reproducible builds",
                            metadata={"dependency": line}
                        )
                        findings.append(finding)
        
        return findings
