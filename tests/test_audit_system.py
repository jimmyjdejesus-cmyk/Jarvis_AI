#!/usr/bin/env python3
"""
Test script for the Jarvis AI audit system.

This script tests the basic functionality of the audit system.
"""

import sys
from pathlib import Path

# Add the jarvis_core directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "jarvis_core"))

from audit.engine import AuditEngine
from audit.models import ScanConfiguration, ScanDepth


def test_audit_system():
    """Test the basic audit system functionality."""
    print("🧪 Testing Jarvis AI Audit System...")
    
    # Create a minimal scan configuration
    config = ScanConfiguration(
        scan_depth=ScanDepth.BASIC,
        include_tests=False,
        exclude_patterns=["__pycache__", "*.pyc", ".git", "venv", ".venv"]
    )
    
    # Initialize the audit engine
    engine = AuditEngine(config)
    
    # Test the current directory
    current_dir = Path(__file__).parent
    print(f"🔍 Scanning directory: {current_dir}")
    
    try:
        # Run the audit
        report = engine.run_audit(current_dir)
        
        # Display results
        print("\n" + "="*80)
        print("🔍 JARVIS AI AUDIT REPORT - TEST RESULTS")
        print("="*80)
        
        print(f"\n📊 SUMMARY")
        print(f"   Report ID: {report.report_id}")
        print(f"   Scan Duration: {report.scan_duration:.2f} seconds")
        print(f"   Files Scanned: {report.total_files_scanned}")
        print(f"   Total Findings: {report.total_findings}")
        print(f"   Risk Score: {report.risk_score:.1f}/10.0")
        
        # Risk level
        risk_emoji = "🚨" if report.risk_score >= 7.0 else "⚠️" if report.risk_score >= 4.0 else "✅"
        risk_level = "HIGH" if report.risk_score >= 7.0 else "MODERATE" if report.risk_score >= 4.0 else "LOW"
        print(f"   Risk Level: {risk_emoji} {risk_level}")
        
        # Findings by category
        if report.findings_by_category:
            print(f"\n📋 FINDINGS BY CATEGORY")
            for category, findings in report.findings_by_category.items():
                if findings:
                    severity_counts = {}
                    for finding in findings:
                        severity = finding.severity.value
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    print(f"   {category.value}: {len(findings)} issues")
                    for severity, count in severity_counts.items():
                        emoji = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "ℹ️"}.get(severity, "•")
                        print(f"      {emoji} {severity}: {count}")
        
        # Recommendations
        if report.recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS")
            for i, recommendation in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {recommendation}")
        
        print(f"\n📝 EXECUTIVE SUMMARY")
        print(f"   {report.summary}")
        print("\n" + "="*80)
        
        print("\n✅ Audit system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Audit system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scanner_individual():
    """Test individual scanners."""
    print("\n🧪 Testing Individual Scanners...")
    
    config = ScanConfiguration()
    current_dir = Path(__file__).parent
    
    # Collect files to scan
    files_to_scan = []
    for file_path in current_dir.rglob("*.py"):
        if "test_audit_system.py" not in str(file_path) and "audit" not in str(file_path):
            files_to_scan.append(file_path)
    
    print(f"📁 Found {len(files_to_scan)} Python files to test scanning")
    
    # Test security scanner
    try:
        from audit.scanner import SecurityScanner
        security_scanner = SecurityScanner(config)
        security_findings = security_scanner.scan_files(files_to_scan[:5])  # Test first 5 files
        print(f"🔒 Security scanner found {len(security_findings)} issues")
        
        # Test code quality scanner
        from audit.scanner import CodeQualityScanner
        quality_scanner = CodeQualityScanner(config)
        quality_findings = quality_scanner.scan_files(files_to_scan[:5])
        print(f"📝 Code quality scanner found {len(quality_findings)} issues")
        
        # Test dependency scanner
        from audit.scanner import DependencyScanner
        dep_scanner = DependencyScanner(config)
        dep_findings = dep_scanner.scan_files(files_to_scan[:5])
        print(f"📦 Dependency scanner found {len(dep_findings)} issues")
        
        print("✅ Individual scanner tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Individual scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Jarvis AI Audit System Tests")
    print("="*80)
    
    # Test the complete audit system
    audit_success = test_audit_system()
    
    # Test individual components
    scanner_success = test_scanner_individual()
    
    print("\n" + "="*80)
    print("🏁 TEST SUMMARY")
    print("="*80)
    print(f"Complete Audit Test: {'✅ PASSED' if audit_success else '❌ FAILED'}")
    print(f"Individual Scanners Test: {'✅ PASSED' if scanner_success else '❌ FAILED'}")
    
    if audit_success and scanner_success:
        print("\n🎉 All tests passed! The audit system is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        sys.exit(1)
