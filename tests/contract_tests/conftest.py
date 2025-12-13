"""
Contract Testing Configuration and Fixtures

This module provides pytest fixtures and configuration for contract testing.
"""

import pytest
import asyncio
import os
from typing import Dict, Any
from pathlib import Path

from .test_api_contracts import APIContractTester
from .test_performance_contracts import PerformanceContractTester


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def base_url():
    """Get base URL for API testing."""
    return os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
def api_key():
    """Get API key for testing."""
    return os.getenv("TEST_API_KEY")


@pytest.fixture
async def api_contract_tester(base_url: str, api_key: str):
    """Create API contract tester instance."""
    tester = APIContractTester(base_url=base_url, api_key=api_key)
    yield tester
    await tester.client.aclose()


@pytest.fixture
async def performance_contract_tester(base_url: str, api_key: str):
    """Create performance contract tester instance."""
    tester = PerformanceContractTester(base_url=base_url, api_key=api_key)
    yield tester
    await tester.close()


@pytest.fixture
def contract_test_data_dir():
    """Get path to contract test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def openapi_spec_path():
    """Get path to OpenAPI specification."""
    return Path(__file__).parent.parent.parent / "openapi.yaml"


@pytest.fixture
def test_endpoints():
    """Define test endpoints for comprehensive testing."""
    return [
        {
            'name': 'health_check',
            'method': 'GET',
            'endpoint': '/health',
            'expected_status': 200,
            'required_fields': ['status', 'timestamp']
        },
        {
            'name': 'list_models',
            'method': 'GET',
            'endpoint': '/models',
            'expected_status': 200,
            'required_fields': ['models']
        },
        {
            'name': 'chat_completion',
            'method': 'POST',
            'endpoint': '/chat',
            'expected_status': 200,
            'payload': {
                'messages': [{'role': 'user', 'content': 'Hello'}],
                'model': 'test-model'
            },
            'required_fields': ['content', 'model']
        },
        {
            'name': 'list_agents',
            'method': 'GET',
            'endpoint': '/agents',
            'expected_status': 200,
            'required_fields': ['agents']
        },
        {
            'name': 'monitoring_metrics',
            'method': 'GET',
            'endpoint': '/monitoring/metrics',
            'expected_status': 200,
            'required_fields': ['metrics']
        }
    ]


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for different endpoint types."""
    return {
        'health': {
            'max_response_time_ms': 100,
            'min_success_rate': 0.99
        },
        'models': {
            'max_response_time_ms': 200,
            'min_success_rate': 0.98
        },
        'chat': {
            'max_response_time_ms': 5000,
            'min_success_rate': 0.95
        },
        'agents': {
            'max_response_time_ms': 1000,
            'min_success_rate': 0.98
        },
        'monitoring': {
            'max_response_time_ms': 500,
            'min_success_rate': 0.98
        }
    }


@pytest.fixture
def error_scenarios():
    """Define error scenarios for testing."""
    return [
        {
            'name': 'invalid_chat_request',
            'method': 'POST',
            'endpoint': '/chat',
            'payload': {'invalid': 'data'},
            'expected_status': [400, 422]
        },
        {
            'name': 'missing_required_fields',
            'method': 'POST',
            'endpoint': '/chat',
            'payload': {'messages': []},
            'expected_status': [400, 422]
        },
        {
            'name': 'nonexistent_endpoint',
            'method': 'GET',
            'endpoint': '/nonexistent',
            'expected_status': [404]
        }
    ]


@pytest.fixture
def load_test_config():
    """Configuration for load testing."""
    return {
        'concurrent_requests': [1, 5, 10],
        'duration_seconds': 5,
        'ramp_up_time': 1
    }


@pytest.fixture
def contract_violation_severity_levels():
    """Define severity levels for contract violations."""
    return {
        'CRITICAL': ['Missing required fields', 'Invalid data types', 'Security violations'],
        'HIGH': ['Performance threshold exceeded', 'Response format changes'],
        'MEDIUM': ['Optional field missing', 'Response time degradation'],
        'LOW': ['Documentation inconsistencies', 'Minor format variations']
    }
