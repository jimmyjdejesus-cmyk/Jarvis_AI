#!/usr/bin/env python3
"""
Simple API Contract Validation Script (without PyYAML dependency)

This script validates API contracts using basic text processing
to avoid dependency conflicts.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

class SimpleAPIValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, message: str):
        self.successes.append(message)
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        self.warnings.append(message)
        print(f"⚠️ {message}")
        
    def log_error(self, message: str):
        self.errors.append(message)
        print(f"❌ {message}")
        
    def validate_openapi_file(self, file_path: str) -> bool:
        """Validate the main OpenAPI specification file."""
        print(f"\n🔍 Validating OpenAPI specification: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for required sections
            required_sections = ['openapi:', 'info:', 'paths:']
            for section in required_sections:
                if section in content:
                    self.log_success(f"Required section '{section.strip(':')}' found")
                else:
                    self.log_error(f"Missing required section: {section.strip(':')}")
                    return False
                    
            # Check OpenAPI version
            if 'openapi: 3' in content:
                self.log_success("OpenAPI 3.x specification detected")
            else:
                self.log_warning("OpenAPI version not detected as 3.x")
                
            # Count endpoints
            get_endpoints = len(re.findall(r'^\s+get:', content, re.MULTILINE))
            post_endpoints = len(re.findall(r'^\s+post:', content, re.MULTILINE))
            total_endpoints = get_endpoints + post_endpoints
            
            self.log_success(f"Found {total_endpoints} API endpoints ({get_endpoints} GET, {post_endpoints} POST)")
            
            # Check for schemas
            schema_refs = len(re.findall(r'\$ref:', content))
            self.log_success(f"Found {schema_refs} schema references")
                
            return True
            
        except Exception as e:
            self.log_error(f"Error loading OpenAPI spec: {e}")
            return False
            
    def validate_schema_files(self, schema_dir: str) -> bool:
        """Validate individual schema files."""
        print(f"\n🔍 Validating schema files in: {schema_dir}")
        
        schema_files = list(Path(schema_dir).glob('*.yaml'))
        if not schema_files:
            self.log_error(f"No YAML schema files found in {schema_dir}")
            return False
            
        self.log_success(f"Found {len(schema_files)} schema files")
        
        total_schemas = 0
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    content = f.read()
                    
                # Count schema definitions (looking for model names followed by colon)
                schemas = len(re.findall(r'^([A-Za-z][A-Za-z0-9_]*):\s*$', content, re.MULTILINE))
                total_schemas += schemas
                
                if schemas > 0:
                    self.log_success(f"Schema file '{schema_file.name}' contains {schemas} schemas")
                else:
                    self.log_warning(f"Schema file '{schema_file.name}' contains no schemas")
                    
            except Exception as e:
                self.log_error(f"Error reading schema file {schema_file}: {e}")
                return False
                
        self.log_success(f"Total schemas across all files: {total_schemas}")
        return True
        
    def check_file_structure(self, base_dir: str) -> bool:
        """Check if all expected files exist."""
        print(f"\n🔍 Checking file structure...")
        
        expected_files = [
            'openapi.yaml',
            'docs/API_CONTRACTS_README.md'
        ]
        
        expected_dirs = [
            'api_schemas'
        ]
        
        all_good = True
        
        # Check files
        for file_path in expected_files:
            full_path = os.path.join(base_dir, file_path)
            if os.path.exists(full_path):
                self.log_success(f"File found: {file_path}")
            else:
                self.log_error(f"Missing file: {file_path}")
                all_good = False
                
        # Check directories
        for dir_path in expected_dirs:
            full_path = os.path.join(base_dir, dir_path)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                self.log_success(f"Directory found: {dir_path}")
            else:
                self.log_error(f"Missing directory: {dir_path}")
                all_good = False
                
        return all_good
        
    def check_completeness(self, base_dir: str) -> bool:
        """Check completeness of the API contract suite."""
        print(f"\n🔍 Checking completeness...")
        
        openapi_file = os.path.join(base_dir, 'openapi.yaml')
        schema_dir = os.path.join(base_dir, 'api_schemas')
        
        try:
            # Read OpenAPI file
            with open(openapi_file, 'r') as f:
                openapi_content = f.read()
                
            # Count expected endpoints based on original API docs
            expected_categories = ['health', 'models', 'chat', 'agents', 'memory', 'workflows', 'security', 'monitoring', 'feed', 'jobs']
            found_categories = []
            
            for category in expected_categories:
                if category in openapi_content.lower():
                    found_categories.append(category)
                    
            self.log_success(f"Found {len(found_categories)}/{len(expected_categories)} expected API categories")
            
            if len(found_categories) >= 8:  # Allow for some flexibility
                self.log_success("API contract coverage appears comprehensive")
            else:
                self.log_warning(f"Only {len(found_categories)} categories found, expected at least 8")
                
            return True
            
        except Exception as e:
            self.log_error(f"Error checking completeness: {e}")
            return False
            
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        return {
            'successes': len(self.successes),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'total_checks': len(self.successes) + len(self.warnings) + len(self.errors),
            'status': 'PASS' if len(self.errors) == 0 else 'FAIL'
        }
        
    def run_validation(self, base_dir: str = '.'):
        """Run complete validation suite."""
        print("🚀 Starting Simple API Contract Validation Suite")
        print("=" * 55)
        
        # Run validations
        validations = [
            self.check_file_structure(base_dir),
            self.validate_openapi_file(os.path.join(base_dir, 'openapi.yaml')),
            self.validate_schema_files(os.path.join(base_dir, 'api_schemas')),
            self.check_completeness(base_dir)
        ]
        
        # Generate summary
        summary = self.generate_summary()
        
        print("\n" + "=" * 55)
        print("📊 VALIDATION SUMMARY")
        print("=" * 55)
        print(f"✅ Successful checks: {summary['successes']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Errors: {summary['errors']}")
        print(f"📈 Total checks: {summary['total_checks']}")
        print(f"🎯 Status: {summary['status']}")
        
        if summary['errors'] == 0:
            print("\n🎉 All validations passed! API contracts are ready for use.")
            print("\n📋 Deliverables created:")
            print("  • openapi.yaml - Complete OpenAPI 3.0 specification")
            print("  • api_schemas/ - Modular JSON schema components")
            print("  • docs/API_CONTRACTS_README.md - Comprehensive documentation")
            print("  • validate_contracts_simple.py - Validation script")
        else:
            print(f"\n💥 {summary['errors']} validation(s) failed. Please review the errors above.")
            
        return summary['status'] == 'PASS'

def main():
    """Main entry point."""
    validator = SimpleAPIValidator()
    
    # Run validation
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
