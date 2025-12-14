#!/usr/bin/env python3
"""
API Contract Validation Script

This script validates API contracts against the OpenAPI specification
and checks consistency between documentation formats.
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Any

class APIValidator:
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
                spec = yaml.safe_load(f)
                
            # Check required fields
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field in spec:
                    self.log_success(f"Required field '{field}' present")
                else:
                    self.log_error(f"Missing required field: {field}")
                    return False
                    
            # Check OpenAPI version
            if spec.get('openapi', '').startswith('3.'):
                self.log_success("OpenAPI 3.x specification detected")
            else:
                self.log_warning(f"Unexpected OpenAPI version: {spec.get('openapi')}")
                
            # Check paths
            paths = spec.get('paths', {})
            self.log_success(f"Found {len(paths)} API endpoints")
            
            # Check components
            components = spec.get('components', {})
            if 'schemas' in components:
                self.log_success(f"Found {len(components['schemas'])} schema definitions")
            else:
                self.log_warning("No schemas found in components")
                
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
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schemas = yaml.safe_load(f)
                    
                if schemas:
                    self.log_success(f"Schema file '{schema_file.name}' loaded successfully ({len(schemas)} schemas)")
                else:
                    self.log_warning(f"Schema file '{schema_file.name}' is empty")
                    
            except Exception as e:
                self.log_error(f"Error loading schema file {schema_file}: {e}")
                return False
                
        return True
        
    def check_schema_references(self, openapi_file: str, schema_dir: str) -> bool:
        """Check if OpenAPI references match existing schema files."""
        print(f"\n🔍 Checking schema references...")
        
        try:
            with open(openapi_file, 'r') as f:
                content = f.read()
                
            # Find all schema references
            schema_refs = re.findall(r'\$ref: [\'"](\./api_schemas/[^\'"]+)[\'"]', content)
            
            if not schema_refs:
                self.log_warning("No schema references found in OpenAPI file")
                return True
                
            self.log_success(f"Found {len(schema_refs)} schema references")
            
            # Check if referenced files exist
            missing_files = []
            for ref in schema_refs:
                ref_path = os.path.join(os.path.dirname(openapi_file), ref)
                if not os.path.exists(ref_path):
                    missing_files.append(ref)
                    
            if missing_files:
                self.log_error(f"Missing schema files: {missing_files}")
                return False
            else:
                self.log_success("All referenced schema files exist")
                
            return True
            
        except Exception as e:
            self.log_error(f"Error checking schema references: {e}")
            return False
            
    def check_consistency_with_docs(self, openapi_file: str, docs_file: str) -> bool:
        """Check consistency between OpenAPI spec and documentation."""
        print(f"\n🔍 Checking consistency with documentation...")
        
        try:
            # Load OpenAPI spec
            with open(openapi_file, 'r') as f:
                spec = yaml.safe_load(f)
                
            paths = spec.get('paths', {})
            endpoints = list(paths.keys())
            
            # Load original API docs
            with open(docs_file, 'r') as f:
                docs_content = f.read()
                
            # Check if all endpoints from OpenAPI are documented
            undocumented = []
            for endpoint in endpoints:
                # Simple check - look for endpoint path in docs
                if endpoint.replace('/', '\\/') not in docs_content and endpoint not in docs_content:
                    undocumented.append(endpoint)
                    
            if undocumented:
                self.log_warning(f"Endpoints not in original docs: {undocumented}")
            else:
                self.log_success("All OpenAPI endpoints found in documentation")
                
            return True
            
        except Exception as e:
            self.log_error(f"Error checking consistency: {e}")
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
        print("🚀 Starting API Contract Validation Suite")
        print("=" * 50)
        
        # Set up paths
        openapi_file = os.path.join(base_dir, 'openapi.yaml')
        schema_dir = os.path.join(base_dir, 'api_schemas')
        docs_file = os.path.join(base_dir, 'docs', 'API_V1.md')
        
        # Run validations
        validations = [
            self.validate_openapi_file(openapi_file),
            self.validate_schema_files(schema_dir),
            self.check_schema_references(openapi_file, schema_dir),
            self.check_consistency_with_docs(openapi_file, docs_file)
        ]
        
        # Generate summary
        summary = self.generate_summary()
        
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        print(f"✅ Successful checks: {summary['successes']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Errors: {summary['errors']}")
        print(f"📈 Total checks: {summary['total_checks']}")
        print(f"🎯 Status: {summary['status']}")
        
        if summary['errors'] == 0:
            print("\n🎉 All validations passed! API contracts are ready for use.")
        else:
            print(f"\n💥 {summary['errors']} validation(s) failed. Please review the errors above.")
            
        return summary['status'] == 'PASS'

def main():
    """Main entry point."""
    validator = APIValidator()
    
    # Run validation
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
