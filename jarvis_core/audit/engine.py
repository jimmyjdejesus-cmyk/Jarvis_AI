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
Audit Engine - Core orchestration for the AdaptiveMind AI audit system.

This module provides the main AuditEngine class that coordinates all scanning
operations and generates comprehensive audit reports.
"""

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

from .models import (
    AuditFinding, AuditReport, ScanConfiguration, 
    AuditCategory, SeverityLevel
)
from .scanner import SecurityScanner, CodeQualityScanner, DependencyScanner


class AuditEngine:
    """
    Main audit engine that orchestrates comprehensive code audits.
    
    The AuditEngine coordinates multiple specialized scanners to provide
    complete coverage of security vulnerabilities, code quality issues,
    performance bottlenecks, and compliance violations.
    """
    
    def __init__(self, config: Optional[ScanConfiguration] = None):
        """
        Initialize the audit engine.
        
        Args:
            config: Optional scan configuration. Uses defaults if not provided.
        """
        self.config = config or ScanConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize scanners
        self.security_scanner = SecurityScanner(self.config)
        self.code_quality_scanner = CodeQualityScanner(self.config)
        self.dependency_scanner = DependencyScanner(self.config)
        
        # Track scan state
        self._scan_in_progress = False
        self._current_scan_id: Optional[str] = None
    
    def run_audit(self, target_path: Path, output_dir: Optional[Path] = None) -> AuditReport:
        """
        Run a comprehensive audit on the target directory.
        
        Args:
            target_path: Path to the directory or file to audit
            output_dir: Optional directory to save audit artifacts
            
        Returns:
            Comprehensive audit report with all findings
        """
        if self._scan_in_progress:
            raise RuntimeError("Audit scan is already in progress")
        
        self._scan_in_progress = True
        self._current_scan_id = str(uuid.uuid4())
        
        start_time = time.time()
        all_findings: List[AuditFinding] = []
        files_scanned = 0
        
        try:
            self.logger.info(f"Starting comprehensive audit of {target_path}")
            
            # Ensure target path exists
            if not target_path.exists():
                raise FileNotFoundError(f"Target path does not exist: {target_path}")
            
            # Collect all Python files to scan
            files_to_scan = self._collect_files_to_scan(target_path)
            files_scanned = len(files_to_scan)
            
            self.logger.info(f"Found {files_scanned} files to scan")
            
            # Run security scanning
            self.logger.info("Running security vulnerability scan...")
            security_findings = self.security_scanner.scan_files(files_to_scan)
            all_findings.extend(security_findings)
            
            # Run code quality scanning
            self.logger.info("Running code quality analysis...")
            quality_findings = self.code_quality_scanner.scan_files(files_to_scan)
            all_findings.extend(quality_findings)
            
            # Run dependency scanning
            self.logger.info("Running dependency vulnerability scan...")
            dependency_findings = self.dependency_scanner.scan_files(files_to_scan)
            all_findings.extend(dependency_findings)
            
            # Calculate scan metrics
            scan_duration = time.time() - start_time
            total_findings = len(all_findings)
            
            # Group findings by category
            findings_by_category = self._group_findings_by_category(all_findings)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(all_findings)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_findings)
            
            # Create compliance status
            compliance_status = self._assess_compliance(all_findings)
            
            # Create summary
            summary = self._generate_summary(total_findings, risk_score, compliance_status)
            
            # Create comprehensive report
            report = AuditReport(
                report_id=self._current_scan_id,
                scan_duration=scan_duration,
                total_files_scanned=files_scanned,
                total_findings=total_findings,
                findings_by_category=findings_by_category,
                risk_score=risk_score,
                compliance_status=compliance_status,
                recommendations=recommendations,
                summary=summary
            )
            
            # Save report if output directory specified
            if output_dir:
                self._save_report(report, output_dir)
            
            self.logger.info(f"Audit completed. Found {total_findings} issues in {files_scanned} files")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Audit failed: {e}")
            raise
        finally:
            self._scan_in_progress = False
            self._current_scan_id = None
    
    def _collect_files_to_scan(self, target_path: Path) -> List[Path]:
        """
        Collect all Python files that should be scanned based on configuration.
        
        Args:
            target_path: Root path to scan
            
        Returns:
            List of Python file paths to scan
        """
        files_to_scan = []
        
        if target_path.is_file():
            if target_path.suffix == '.py' and self._should_include_file(target_path):
                files_to_scan.append(target_path)
            return files_to_scan
        
        # Recursively collect Python files
        for file_path in target_path.rglob('*.py'):
            if self._should_include_file(file_path):
                files_to_scan.append(file_path)
        
        return files_to_scan
    
    def _should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included in scanning based on configuration.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be included
        """
        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if file_path.match(pattern):
                return False
        
        # Check if tests should be included
        if not self.config.include_tests:
            if 'test' in str(file_path).lower() or 'spec' in str(file_path).lower():
                return False
        
        return True
    
    def _group_findings_by_category(self, findings: List[AuditFinding]) -> Dict[AuditCategory, List[AuditFinding]]:
        """Group findings by their category."""
        grouped = {}
        for finding in findings:
            category = finding.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(finding)
        return grouped
    
    def _calculate_risk_score(self, findings: List[AuditFinding]) -> float:
        """
        Calculate overall risk score based on findings.
        
        Args:
            findings: List of all audit findings
            
        Returns:
            Risk score between 0.0 and 10.0
        """
        if not findings:
            return 0.0
        
        severity_weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 7.5,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 1.0
        }
        
        total_weighted_score = 0.0
        total_count = 0
        
        for finding in findings:
            weight = severity_weights[finding.severity]
            # Use CVSS score if available, otherwise use severity weight
            score = finding.cvss_score if finding.cvss_score is not None else weight
            total_weighted_score += score
            total_count += 1
        
        return min(10.0, total_weighted_score / total_count if total_count > 0 else 0.0)
    
    def _generate_recommendations(self, findings: List[AuditFinding]) -> List[str]:
        """
        Generate prioritized recommendations based on findings.
        
        Args:
            findings: List of audit findings
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        # Group findings by severity
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
        high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
        medium_findings = [f for f in findings if f.severity == SeverityLevel.MEDIUM]
        
        # Generate recommendations based on critical findings
        if critical_findings:
            security_critical = [f for f in critical_findings if f.category == AuditCategory.SECURITY]
            if security_critical:
                recommendations.append("🚨 URGENT: Address all critical security vulnerabilities immediately")
            
            performance_critical = [f for f in critical_findings if f.category == AuditCategory.PERFORMANCE]
            if performance_critical:
                recommendations.append("⚡ CRITICAL: Optimize critical performance bottlenecks affecting system stability")
        
        # Generate recommendations based on high findings
        if high_findings:
            recommendations.append("🔒 HIGH: Review and address high-priority security and code quality issues")
        
        # Generate category-specific recommendations
        security_findings = [f for f in findings if f.category == AuditCategory.SECURITY]
        if security_findings:
            recommendations.append("🛡️ SECURITY: Implement security best practices and fix vulnerabilities")
        
        code_quality_findings = [f for f in findings if f.category == AuditCategory.CODE_QUALITY]
        if code_quality_findings:
            recommendations.append("📝 CODE QUALITY: Improve code maintainability and reduce technical debt")
        
        dependency_findings = [f for f in findings if f.category == AuditCategory.DEPENDENCY]
        if dependency_findings:
            recommendations.append("📦 DEPENDENCIES: Update vulnerable dependencies and review dependency management")
        
        if not recommendations:
            recommendations.append("✅ No critical issues found. Continue regular maintenance and monitoring.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _assess_compliance(self, findings: List[AuditFinding]) -> Dict[str, bool]:
        """
        Assess compliance with various security standards.
        
        Args:
            findings: List of audit findings
            
        Returns:
            Dictionary mapping compliance standards to their status
        """
        compliance_status = {}
        
        # OWASP compliance - check for OWASP Top 10 issues
        owasp_violations = [f for f in findings if f.cwe_id and f.cwe_id.startswith('A')]
        compliance_status["OWASP"] = len(owasp_violations) == 0
        
        # NIST compliance - check for high/critical security issues
        nist_violations = [f for f in findings 
                          if f.category == AuditCategory.SECURITY 
                          and f.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
        compliance_status["NIST"] = len(nist_violations) == 0
        
        # Code quality compliance
        quality_violations = [f for f in findings if f.category == AuditCategory.CODE_QUALITY]
        compliance_status["CODE_QUALITY"] = len(quality_violations) < 10  # Allow some quality issues
        
        # Performance compliance
        performance_violations = [f for f in findings if f.category == AuditCategory.PERFORMANCE]
        compliance_status["PERFORMANCE"] = len(performance_violations) < 5  # Allow some performance issues
        
        return compliance_status
    
    def _generate_summary(self, total_findings: int, risk_score: float, compliance_status: Dict[str, bool]) -> str:
        """
        Generate executive summary of the audit.
        
        Args:
            total_findings: Total number of findings
            risk_score: Overall risk score
            compliance_status: Compliance assessment results
            
        Returns:
            Executive summary string
        """
        summary_parts = []
        
        # Overall assessment
        if risk_score >= 7.0:
            summary_parts.append("🚨 HIGH RISK: Significant security and quality issues detected")
        elif risk_score >= 4.0:
            summary_parts.append("⚠️ MODERATE RISK: Some security and quality improvements needed")
        else:
            summary_parts.append("✅ LOW RISK: Generally good security and code quality")
        
        # Findings summary
        summary_parts.append(f"Found {total_findings} issues requiring attention")
        
        # Compliance summary
        passed_standards = sum(1 for status in compliance_status.values() if status)
        total_standards = len(compliance_status)
        summary_parts.append(f"Compliance: {passed_standards}/{total_standards} standards passed")
        
        # Key recommendations
        critical_compliance = [std for std, status in compliance_status.items() if not status]
        if critical_compliance:
            summary_parts.append(f"Focus areas: {', '.join(critical_compliance)} compliance")
        
        return " ".join(summary_parts)
    
    def _save_report(self, report: AuditReport, output_dir: Path) -> None:
        """
        Save audit report to output directory.
        
        Args:
            report: Audit report to save
            output_dir: Directory to save the report
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        import json
        report_file = output_dir / f"audit_report_{report.report_id}.json"
        with open(report_file, 'w') as f:
            # Convert to dict for JSON serialization
            report_dict = report.dict()
            # Handle datetime serialization
            report_dict['scan_timestamp'] = report.scan_timestamp.isoformat()
            for category, findings in report_dict['findings_by_category'].items():
                for finding in findings:
                    finding['timestamp'] = finding['timestamp'].isoformat()
            json.dump(report_dict, f, indent=2)
        
        self.logger.info(f"Audit report saved to {report_file}")
    
    def get_scan_status(self) -> Dict[str, any]:
        """
        Get current scan status.
        
        Returns:
            Dictionary with current scan status information
        """
        return {
            "scan_in_progress": self._scan_in_progress,
            "current_scan_id": self._current_scan_id,
            "config": self.config.dict()
        }
