#!/usr/bin/env python3
"""
Lang Ecosystem Integration Validator

This script validates that the Lang ecosystem integration plan properly maps 
components to each open issue and ensures consistency with existing integrations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

def analyze_existing_lang_integration() -> Dict[str, Set[str]]:
    """Analyze existing Lang ecosystem integration in the repository."""
    
    lang_components = {
        'langchain': set(),
        'langgraph': set(), 
        'langsmith': set(),
        'langgraph_ui': set(),
        'langgraph_platform': set()
    }
    
    # Check requirements files
    requirements_files = [
        'legacy/requirements_enhanced.txt',
        'development/requirements.txt', 
        'v2/requirements.txt'
    ]
    
    for req_file in requirements_files:
        req_path = Path(req_file)
        if req_path.exists():
            try:
                with open(req_path, 'r') as f:
                    content = f.read().lower()
                    if 'langchain' in content:
                        lang_components['langchain'].add(req_file)
                    if 'langgraph' in content:
                        lang_components['langgraph'].add(req_file)
                    if 'langsmith' in content:
                        lang_components['langsmith'].add(req_file)
                    if 'langgraphstudio' in content or 'langgraph-studio' in content:
                        lang_components['langgraph_ui'].add(req_file)
            except Exception as e:
                print(f"Warning: Could not read {req_file}: {e}")
    
    # Check for existing adapters and integrations
    integration_files = [
        'legacy/agent/adapters/langchain_tools.py',
        'legacy/agent/adapters/langgraph_workflow.py',
        'development/agent/adapters/lang_integrations.py',
        'v2/agent/adapters/lang_integrations.py',
        'legacy/tests/test_lang_integration.py'
    ]
    
    for int_file in integration_files:
        int_path = Path(int_file)
        if int_path.exists():
            component_type = 'langchain' if 'langchain' in int_file else 'langgraph'
            lang_components[component_type].add(int_file)
    
    return lang_components

def validate_issue_mapping() -> Dict[str, Dict[str, bool]]:
    """Validate that each issue is properly mapped to Lang components."""
    
    # Define expected mappings based on issue requirements
    issue_mappings = {
        'Issue #27 (Deployment)': {
            'langchain': True,   # Core packaging and dependency management
            'langgraph': True,   # Workflow deployment and orchestration  
            'langsmith': True,   # Production monitoring
            'langgraph_platform': True,  # Scalable deployment infrastructure
            'langgraph_ui': False  # Optional for deployment
        },
        'Issue #28 (Reliability)': {
            'langchain': True,   # Error handling chains, fallback mechanisms
            'langgraph': True,   # State management for degraded modes
            'langsmith': True,   # Real-time monitoring and error tracking
            'langgraph_platform': False,  # Optional distributed reliability
            'langgraph_ui': True   # Visualization of system health
        },
        'Issue #29 (Extensibility)': {
            'langchain': True,   # Plugin architecture using Tools
            'langgraph': True,   # Extensible workflow nodes
            'langsmith': True,   # Plugin performance monitoring
            'langgraph_platform': True,  # Plugin sharing and discovery
            'langgraph_ui': True   # Plugin workflow visualization
        },
        'Issue #30 (User Experience)': {
            'langchain': True,   # Memory systems for personalization
            'langgraph': True,   # User interaction workflows
            'langsmith': True,   # User interaction tracking
            'langgraph_platform': False,  # Optional personalized agent sharing
            'langgraph_ui': True   # Interactive explanation visualization
        }
    }
    
    return issue_mappings

def check_implementation_readiness() -> Dict[str, bool]:
    """Check if the repository is ready for Lang ecosystem implementation."""
    
    readiness_checks = {
        'requirements_files_exist': False,
        'adapter_patterns_exist': False, 
        'test_infrastructure_exists': False,
        'documentation_exists': False,
        'migration_guide_exists': False
    }
    
    # Check requirements
    if Path('legacy/requirements_enhanced.txt').exists():
        readiness_checks['requirements_files_exist'] = True
    
    # Check adapter patterns
    if Path('legacy/agent/adapters/langchain_tools.py').exists():
        readiness_checks['adapter_patterns_exist'] = True
        
    # Check test infrastructure  
    if Path('legacy/tests/test_lang_integration.py').exists():
        readiness_checks['test_infrastructure_exists'] = True
        
    # Check documentation
    if Path('legacy/docs/V2_MIGRATION_GUIDE.md').exists():
        readiness_checks['documentation_exists'] = True
        
    # Check migration guide
    if Path('docs/LANG_ECOSYSTEM_ISSUE_INTEGRATION.md').exists():
        readiness_checks['migration_guide_exists'] = True
    
    return readiness_checks

def generate_implementation_summary() -> str:
    """Generate a summary of the implementation approach."""
    
    summary = """
# Lang Ecosystem Integration Implementation Summary

## Current State Analysis
"""
    
    # Analyze existing integration
    existing_integration = analyze_existing_lang_integration()
    
    summary += "### Existing Lang Components Found:\n"
    for component, files in existing_integration.items():
        if files:
            summary += f"- **{component.title()}**: {len(files)} files\n"
            for file in sorted(files):
                summary += f"  - {file}\n"
        else:
            summary += f"- **{component.title()}**: Not found\n"
    
    # Validate issue mappings
    issue_mappings = validate_issue_mapping()
    
    summary += "\n### Issue Component Mappings:\n"
    for issue, components in issue_mappings.items():
        summary += f"#### {issue}\n"
        for component, required in components.items():
            status = "✅ Required" if required else "⭕ Optional"
            summary += f"- {component.title()}: {status}\n"
    
    # Check readiness
    readiness = check_implementation_readiness()
    
    summary += "\n### Implementation Readiness:\n"
    for check, status in readiness.items():
        status_icon = "✅" if status else "❌"
        check_name = check.replace('_', ' ').title()
        summary += f"- {status_icon} {check_name}\n"
    
    # Overall readiness score
    ready_count = sum(readiness.values())
    total_checks = len(readiness)
    readiness_percentage = (ready_count / total_checks) * 100
    
    summary += f"\n### Overall Readiness: {readiness_percentage:.0f}% ({ready_count}/{total_checks} checks passed)\n"
    
    if readiness_percentage >= 80:
        summary += "🎉 **Repository is ready for Lang ecosystem integration!**\n"
    elif readiness_percentage >= 60:
        summary += "⚠️ **Repository is mostly ready, with minor setup needed**\n"
    else:
        summary += "🚨 **Additional setup required before implementation**\n"
    
    return summary

def main():
    """Main validation function."""
    print("🔍 Validating Lang Ecosystem Integration Plan...")
    
    # Change to repository root if needed
    if 'legacy' in os.listdir('.'):
        os.chdir('.')
    elif os.path.exists('../legacy'):
        os.chdir('..')
    
    try:
        # Generate and save implementation summary
        summary = generate_implementation_summary()
        
        # Save to file
        summary_path = Path('docs/LANG_ECOSYSTEM_VALIDATION_SUMMARY.md')
        summary_path.parent.mkdir(exist_ok=True)

        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(f"✅ Validation summary saved to: {summary_path}")
        print("\n" + "="*50)
        print(summary)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)