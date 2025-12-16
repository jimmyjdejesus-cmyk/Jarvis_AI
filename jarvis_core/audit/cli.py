"""
Command-line interface for the Jarvis AI audit system.

Provides a simple CLI for running comprehensive code audits and generating reports.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .engine import AuditEngine
from .models import ScanConfiguration, ScanDepth


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def create_scan_config(args) -> ScanConfiguration:
    """
    Create scan configuration from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Configured ScanConfiguration
    """
    config = ScanConfiguration()
    
    # Set scan depth
    if args.scan_depth:
        config.scan_depth = ScanDepth(args.scan_depth.upper())
    
    # Include tests if requested
    if args.include_tests:
        config.include_tests = True
    
    # Add exclude patterns
    if args.exclude:
        config.exclude_patterns.extend(args.exclude)
    
    # Set security standards
    if args.standards:
        config.security_standards = args.standards.split(',')
    
    return config


def run_audit(args) -> int:
    """
    Run the audit with given arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, 1 for errors)
    """
    try:
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Validate target path
        target_path = Path(args.target)
        if not target_path.exists():
            logger.error(f"Target path does not exist: {target_path}")
            return 1
        
        # Create scan configuration
        config = create_scan_config(args)
        logger.info(f"Scan configuration: {config}")
        
        # Initialize audit engine
        engine = AuditEngine(config)
        
        # Determine output directory
        output_dir = None
        if args.output:
            output_dir = Path(args.output)
        
        # Run audit
        logger.info(f"Starting audit of {target_path}")
        report = engine.run_audit(target_path, output_dir)
        
        # Display results
        print_audit_summary(report)
        
        # Save report if output specified
        if output_dir:
            logger.info(f"Full report saved to {output_dir}")
        
        # Return exit code based on severity
        return 0 if report.risk_score < 7.0 else 1
        
    except Exception as e:
        logging.error(f"Audit failed: {e}")
        return 1


def print_audit_summary(report) -> None:
    """
    Print a formatted summary of the audit report.
    
    Args:
        report: AuditReport to display
    """
    print("\n" + "="*80)
    print("🔍 JARVIS AI AUDIT REPORT")
    print("="*80)
    
    # Summary
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
    
    # Compliance status
    if report.compliance_status:
        print(f"\n✅ COMPLIANCE STATUS")
        for standard, status in report.compliance_status.items():
            status_emoji = "✅" if status else "❌"
            print(f"   {status_emoji} {standard}: {'PASSED' if status else 'FAILED'}")
    
    # Recommendations
    if report.recommendations:
        print(f"\n💡 TOP RECOMMENDATIONS")
        for i, recommendation in enumerate(report.recommendations[:5], 1):
            print(f"   {i}. {recommendation}")
    
    print(f"\n📝 EXECUTIVE SUMMARY")
    print(f"   {report.summary}")
    print("\n" + "="*80)


def list_findings(args) -> int:
    """
    List findings from a saved audit report.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    try:
        import json
        
        report_file = Path(args.report_file)
        if not report_file.exists():
            print(f"Report file not found: {report_file}")
            return 1
        
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        # Convert back to report object (simplified for CLI)
        print(f"\n📋 AUDIT FINDINGS")
        print(f"   Report: {report_data.get('report_id', 'Unknown')}")
        print(f"   Total Findings: {report_data.get('total_findings', 0)}")
        
        findings_by_category = report_data.get('findings_by_category', {})
        
        if args.category:
            # Show specific category
            category_findings = findings_by_category.get(args.category.upper(), [])
            print(f"\n🎯 {args.category.upper()} FINDINGS ({len(category_findings)}):")
            for finding in category_findings:
                print(f"   📁 {finding.get('file_path', 'Unknown')}")
                print(f"      Line {finding.get('line_number', 'N/A')}: {finding.get('title', 'Unknown')}")
                print(f"      Severity: {finding.get('severity', 'Unknown')}")
                print(f"      {finding.get('description', 'No description')}")
                print()
        else:
            # Show all findings summary
            for category, findings in findings_by_category.items():
                if findings:
                    print(f"\n🔍 {category} ({len(findings)} findings):")
                    for finding in findings[:3]:  # Show first 3 of each category
                        print(f"   • {finding.get('title', 'Unknown')} - {finding.get('file_path', 'Unknown')}")
                    if len(findings) > 3:
                        print(f"   ... and {len(findings) - 3} more")
        
        return 0
        
    except Exception as e:
        print(f"Failed to list findings: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command line arguments (for testing)
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Jarvis AI Audit System - Comprehensive security and quality scanning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan /path/to/project                    # Basic audit scan
  %(prog)s scan /path/to/project --output ./reports # Scan with output directory
  %(prog)s scan . --scan-depth comprehensive        # Comprehensive scan of current directory
  %(prog)s scan . --include-tests                   # Include test files in scan
  %(prog)s findings ./reports/audit_report_*.json   # List findings from saved report
  %(prog)s findings ./report.json --category SECURITY # Show only security findings
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run audit scan')
    scan_parser.add_argument('target', help='Target directory or file to audit')
    scan_parser.add_argument('-o', '--output', help='Output directory for reports')
    scan_parser.add_argument('-d', '--scan-depth', choices=['basic', 'standard', 'comprehensive'],
                           help='Scan depth level (default: standard)')
    scan_parser.add_argument('-t', '--include-tests', action='store_true',
                           help='Include test files in scanning')
    scan_parser.add_argument('-e', '--exclude', action='append',
                           help='Exclude pattern (can be used multiple times)')
    scan_parser.add_argument('-s', '--standards', help='Comma-separated security standards (e.g., OWASP,NIST)')
    scan_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Enable verbose logging')
    
    # Findings command
    findings_parser = subparsers.add_parser('findings', help='List findings from saved report')
    findings_parser.add_argument('report_file', help='Path to audit report JSON file')
    findings_parser.add_argument('-c', '--category', choices=['SECURITY', 'PERFORMANCE', 'CODE_QUALITY', 'DEPENDENCY', 'API_COMPLIANCE', 'ARCHITECTURE'],
                               help='Filter findings by category')
    
    # Parse arguments
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute appropriate command
    if args.command == 'scan':
        return run_audit(args)
    elif args.command == 'findings':
        return list_findings(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
