"""
Audit data models for Jarvis AI audit system.

This module defines the core data structures used throughout the audit system
including findings, reports, and scan configurations.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AuditCategory(str, Enum):
    """Audit categories for findings classification."""
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    CODE_QUALITY = "CODE_QUALITY"
    DEPENDENCY = "DEPENDENCY"
    API_COMPLIANCE = "API_COMPLIANCE"
    ARCHITECTURE = "ARCHITECTURE"


class SeverityLevel(str, Enum):
    """Severity levels for audit findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ScanDepth(str, Enum):
    """Depth levels for audit scanning."""
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    COMPREHENSIVE = "COMPREHENSIVE"


class AuditFinding(BaseModel):
    """
    Represents a single audit finding or vulnerability.
    
    Attributes:
        id: Unique identifier for the finding
        category: Category of the audit finding
        severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        title: Concise description of the issue
        description: Detailed analysis and context
        file_path: Path to the file containing the issue
        line_number: Specific line number (if applicable)
        remediation: Recommended fix or remediation steps
        cwe_id: Common Weakness Enumeration ID (if security related)
        cvss_score: Common Vulnerability Scoring System score (0.0-10.0)
        timestamp: When the finding was detected
        metadata: Additional finding-specific metadata
    """
    id: str = Field(..., description="Unique identifier for the finding")
    category: AuditCategory = Field(..., description="Category of the audit finding")
    severity: SeverityLevel = Field(..., description="Severity level of the finding")
    title: str = Field(..., description="Concise description of the issue")
    description: str = Field(..., description="Detailed analysis and context")
    file_path: str = Field(..., description="Path to the file containing the issue")
    line_number: Optional[int] = Field(None, description="Specific line number if applicable")
    remediation: str = Field(..., description="Recommended fix or remediation steps")
    cwe_id: Optional[str] = Field(None, description="CWE ID if security related")
    cvss_score: Optional[float] = Field(None, description="CVSS score (0.0-10.0)", ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.now, description="When finding was detected")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True


class AuditReport(BaseModel):
    """
    Comprehensive audit report containing all findings and analysis.
    
    Attributes:
        report_id: Unique identifier for the report
        scan_timestamp: When the scan was performed
        scan_duration: Duration of the scan in seconds
        total_files_scanned: Number of files analyzed
        total_findings: Total number of findings detected
        findings_by_category: Findings grouped by category
        risk_score: Overall risk score (0.0-10.0)
        compliance_status: Status of various compliance standards
        recommendations: Prioritized list of recommendations
        summary: Executive summary of the audit
    """
    report_id: str = Field(..., description="Unique identifier for the report")
    scan_timestamp: datetime = Field(default_factory=datetime.now, description="When scan was performed")
    scan_duration: float = Field(..., description="Duration of scan in seconds")
    total_files_scanned: int = Field(..., description="Number of files analyzed")
    total_findings: int = Field(..., description="Total number of findings")
    findings_by_category: Dict[AuditCategory, List[AuditFinding]] = Field(
        default_factory=dict, description="Findings grouped by category"
    )
    risk_score: float = Field(..., description="Overall risk score (0.0-10.0)", ge=0.0, le=10.0)
    compliance_status: Dict[str, bool] = Field(
        default_factory=dict, description="Compliance status for various standards"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Prioritized list of recommendations"
    )
    summary: str = Field(..., description="Executive summary of the audit")


class ScanConfiguration(BaseModel):
    """
    Configuration for audit scanning operations.
    
    Attributes:
        scan_depth: Level of scanning depth (BASIC, STANDARD, COMPREHENSIVE)
        include_tests: Whether to include test files in scanning
        exclude_patterns: Patterns to exclude from scanning
        security_standards: Security standards to check compliance against
        performance_thresholds: Performance threshold configurations
        code_quality_rules: Code quality rules to enforce
        custom_rules: Custom audit rules and configurations
    """
    scan_depth: ScanDepth = Field(default=ScanDepth.STANDARD, description="Level of scanning depth")
    include_tests: bool = Field(default=False, description="Whether to include test files")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.pyc", "__pycache__", ".git", "node_modules", 
            ".venv", "venv", "build", "dist", ".tox"
        ], description="Patterns to exclude from scanning"
    )
    security_standards: List[str] = Field(
        default_factory=lambda: ["OWASP", "NIST"], description="Security standards to check"
    )
    performance_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "cyclomatic_complexity": 10.0,
            "maintainability_index": 65.0,
            "lines_of_code": 500
        }, description="Performance threshold configurations"
    )
    code_quality_rules: List[str] = Field(
        default_factory=lambda: ["flake8", "pylint", "mypy"], description="Code quality rules"
    )
    custom_rules: Dict[str, Any] = Field(
        default_factory=dict, description="Custom audit rules and configurations"
    )
    
    class Config:
        use_enum_values = True
