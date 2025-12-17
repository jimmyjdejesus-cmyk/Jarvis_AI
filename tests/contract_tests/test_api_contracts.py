# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Comprehensive API Contract Testing Suite

This module implements contract-based testing for all API endpoints,
validating responses against OpenAPI specifications and business rules.
"""

import pytest
import json
import yaml
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import HTTPException
import jsonschema
from jsonschema import validate, ValidationError
import responses
import httpx


class APIContractTester:
    """Main class for API contract testing and validation."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.contract_violations = []
        self.load_openapi_spec()
        
    def load_openapi_spec(self):
        """Load and parse the OpenAPI specification."""
        spec_path = Path(__file__).parent.parent.parent / "openapi.yaml"
        with open(spec_path, 'r') as f:
            self.openapi_spec = yaml.safe_load(f)
        print(f"✅ Loaded OpenAPI spec with {len(self.openapi_spec.get('paths', {}))} endpoints")
        
    async def validate_response_contract(
        self, 
        endpoint: str, 
        method: str, 
        status_code: int, 
        response_data: Dict[str, Any],
        response_headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate a response against the OpenAPI contract.
        
        Returns:
            Dict containing validation results and any violations found
        """
        violations = []
        
        try:
            # Get the OpenAPI path definition
            path_item = self.openapi_spec['paths'].get(endpoint)
            if not path_item:
                violations.append(f"No OpenAPI definition found for {method.upper()} {endpoint}")
                return {'valid': False, 'violations': violations}
                
            # Get the method definition
            method_def = path_item.get(method.lower())
            if not method_def:
                violations.append(f"No OpenAPI definition for {method.upper()} {endpoint}")
                return {'valid': False, 'violations': violations}
                
            # Validate status code
            responses_def = method_def.get('responses', {})
            if str(status_code) not in responses_def and status_code >= 400:
                # 4xx/5xx responses are generally acceptable without specific definitions
                pass
            elif str(status_code) not in responses_def:
                violations.append(f"Undocumented status code {status_code} for {method.upper()} {endpoint}")
                
            # Validate response schema
            if 'content' in responses_def.get(str(status_code), {}):
                content_def = responses_def[str(status_code)]['content'].get('application/json')
                if content_def and 'schema' in content_def:
                    try:
                        schema = content_def['schema']
                        # Handle schema references
                        if '$ref' in schema:
                            schema = self._resolve_schema_reference(schema['$ref'])
                        
                        validate(instance=response_data, schema=schema)
                        print(f"✅ Schema validation passed for {method.upper()} {endpoint}")
                    except ValidationError as e:
                        violations.append(f"Schema validation failed: {e.message}")
                        print(f"❌ Schema validation failed for {method.upper()} {endpoint}: {e.message}")
                        
            # Validate business rules
            business_violations = self._validate_business_rules(endpoint, method, response_data)
            violations.extend(business_violations)
            
        except Exception as e:
            violations.append(f"Contract validation error: {str(e)}")
            
        return {
            'valid': len(violations) == 0,
            'violations': violations
        }
        
    def _resolve_schema_reference(self, ref: str) -> Dict[str, Any]:
        """Resolve schema reference to actual schema definition."""
        if ref.startswith('#/components/schemas/'):
            schema_name = ref.split('/')[-1]
            return self.openapi_spec['components']['schemas'][schema_name]
        return {}
        
    def _validate_business_rules(self, endpoint: str, method: str, response_data: Dict[str, Any]) -> List[str]:
        """Validate business rules specific to each endpoint."""
        violations = []
        
        # Health endpoint rules
        if endpoint == '/health':
            if 'status' not in response_data:
                violations.append("Health endpoint must include 'status' field")
            if 'timestamp' not in response_data:
                violations.append("Health endpoint must include 'timestamp' field")
                
        # Chat endpoint rules
        if endpoint == '/chat' and method.upper() == 'POST':
            if 'content' not in response_data:
                violations.append("Chat response must include 'content' field")
            if 'model' not in response_data:
                violations.append("Chat response must include 'model' field")
                
        # Job endpoint rules
        if endpoint.startswith('/jobs') and method.upper() == 'GET':
            if 'job_id' not in response_data:
                violations.append("Job status response must include 'job_id' field")
            if 'status' not in response_data:
                violations.append("Job status response must include 'status' field")
                
        return violations


class ContractTestSuite:
    """Complete test suite for API contract validation."""
    
    @pytest.fixture
    def api_tester(self):
        return APIContractTester()
        
    @pytest.fixture
    def test_client(self):
        from jarvis_core import build_app
        from jarvis_core.config import AppConfig, MonitoringConfig, PersonaConfig
        
        config = AppConfig(
            personas={
                "generalist": PersonaConfig(
                    name="generalist",
                    description="Balanced assistant",
                    system_prompt="You are a helpful assistant.",
                    max_context_window=2048,
                    routing_hint="general",
                )
            },
            allowed_personas=["generalist"],
            monitoring=MonitoringConfig(enable_metrics_harvest=False),
        )
        app = build_app(config=config)
        with TestClient(app) as client:
            yield client
    
    async def test_all_endpoints_contracts(self, api_tester: APIContractTester):
        """Test all documented endpoints for contract compliance."""
        
        # Test cases for each endpoint
        test_cases = [
            {
                'endpoint': '/health',
                'method': 'GET',
                'expected_status': 200
            },
            {
                'endpoint': '/models',
                'method': 'GET',
                'expected_status': 200
            },
            {
                'endpoint': '/chat',
                'method': 'POST',
                'expected_status': 200,
                'payload': {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": "test-model"
                }
            },
            {
                'endpoint': '/agents',
                'method': 'GET',
                'expected_status': 200
            },
            {
                'endpoint': '/monitoring/metrics',
                'method': 'GET',
                'expected_status': 200
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                # Make request
                headers = {}
                if api_tester.api_key:
                    headers['X-API-Key'] = api_tester.api_key
                    
                response = await api_tester.client.request(
                    method=test_case['method'],
                    url=f"{api_tester.base_url}{test_case['endpoint']}",
                    json=test_case.get('payload'),
                    headers=headers
                )
                
                # Validate contract
                validation_result = await api_tester.validate_response_contract(
                    endpoint=test_case['endpoint'],
                    method=test_case['method'],
                    status_code=response.status_code,
                    response_data=response.json() if response.content else {},
                    response_headers=dict(response.headers)
                )
                
                results.append({
                    'endpoint': test_case['endpoint'],
                    'method': test_case['method'],
                    'status_code': response.status_code,
                    'validation': validation_result
                })
                
                # Assert contract compliance
                assert validation_result['valid'], f"Contract violations for {test_case['endpoint']}: {validation_result['violations']}"
                
            except Exception as e:
                results.append({
                    'endpoint': test_case['endpoint'],
                    'method': test_case['method'],
                    'error': str(e)
                })
                raise
        
        # Print summary
        print("\n📊 Contract Testing Summary:")
        for result in results:
            if 'error' in result:
                print(f"❌ {result['method']} {result['endpoint']}: {result['error']}")
            elif result['validation']['valid']:
                print(f"✅ {result['method']} {result['endpoint']}: Contract compliant")
            else:
                print(f"❌ {result['method']} {result['endpoint']}: {result['validation']['violations']}")
    
    async def test_error_scenarios(self, api_tester: APIContractTester):
        """Test error scenarios for contract compliance."""
        
        error_test_cases = [
            {
                'name': 'Invalid chat request',
                'endpoint': '/chat',
                'method': 'POST',
                'payload': {'invalid': 'data'},
                'expected_status': [422, 400]  # Validation error
            },
            {
                'name': 'Non-existent endpoint',
                'endpoint': '/nonexistent',
                'method': 'GET',
                'expected_status': [404, 422]
            }
        ]
        
        for test_case in error_test_cases:
            try:
                headers = {}
                if api_tester.api_key:
                    headers['X-API-Key'] = api_tester.api_key
                    
                response = await api_tester.client.request(
                    method=test_case['method'],
                    url=f"{api_tester.base_url}{test_case['endpoint']}",
                    json=test_case.get('payload'),
                    headers=headers
                )
                
                # Check if status code is in expected range
                expected_statuses = test_case['expected_status'] if isinstance(test_case['expected_status'], list) else [test_case['expected_status']]
                assert response.status_code in expected_statuses, f"Unexpected status {response.status_code} for {test_case['name']}"
                
                print(f"✅ {test_case['name']}: Correctly returned status {response.status_code}")
                
            except Exception as e:
                print(f"❌ {test_case['name']}: Error - {str(e)}")
                raise


# Property-based testing for API responses
class PropertyBasedTester:
    """Property-based testing for API responses."""
    
    @staticmethod
    def chat_response_properties(response_data: Dict[str, Any]) -> List[str]:
        """Define properties that chat responses must satisfy."""
        violations = []
        
        # Required fields
        if 'content' not in response_data:
            violations.append("Missing required field 'content'")
        elif not isinstance(response_data['content'], str):
            violations.append("Field 'content' must be a string")
            
        if 'model' not in response_data:
            violations.append("Missing required field 'model'")
        elif not isinstance(response_data['model'], str):
            violations.append("Field 'model' must be a string")
            
        # Optional fields validation
        if 'tokens' in response_data and not isinstance(response_data['tokens'], int):
            violations.append("Field 'tokens' must be an integer")
            
        return violations
        
    @staticmethod
    def health_response_properties(response_data: Dict[str, Any]) -> List[str]:
        """Define properties that health responses must satisfy."""
        violations = []
        
        if 'status' not in response_data:
            violations.append("Missing required field 'status'")
        elif response_data['status'] not in ['ok', 'degraded', 'error']:
            violations.append("Status must be one of: ok, degraded, error")
            
        if 'timestamp' not in response_data:
            violations.append("Missing required field 'timestamp'")
        elif not isinstance(response_data['timestamp'], str):
            violations.append("Timestamp must be a string")
            
        return violations


# Test execution functions
async def run_contract_tests():
    """Run all contract tests and generate report."""
    tester = APIContractTester()
    
    print("🚀 Starting Comprehensive API Contract Testing")
    print("=" * 60)
    
    try:
        await tester.test_all_endpoints_contracts()
        await tester.test_error_scenarios()
        print("\n✅ All contract tests passed!")
        
    except Exception as e:
        print(f"\n❌ Contract tests failed: {e}")
        raise
    finally:
        await tester.client.aclose()


if __name__ == "__main__":
    asyncio.run(run_contract_tests())
