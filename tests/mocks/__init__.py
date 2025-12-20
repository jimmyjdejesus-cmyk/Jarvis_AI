# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Centralized mock infrastructure for the AdaptiveMind test suite.

This package provides organized mock objects and fixtures that can be reused
across all test modules. The mocks are organized by responsibility:

- external_dependencies: Mocks for external libraries and services
- api_mocks: HTTP/API client mocks and responses
- agent_mocks: Agent and system component mocks
- shared_fixtures: Reusable pytest fixtures

Usage:
    from tests.mocks import MockAgent, MockHTTPClient
    from tests.mocks.shared_fixtures import client_fixture
"""

from .external_dependencies import *
from .api_mocks import *
from .agent_mocks import *
from .shared_fixtures import *

__all__ = [
    # External dependencies
    "MockNeo4jDriver",
    "MockPydanticModel", 
    "MockNetworkX",
    "MockChromaDB",
    "MockKeyring",
    
    # API mocks
    "MockHTTPClient",
    "MockResponse",
    "MockWebSocket",
    
    # Agent mocks
    "MockAgent",
    "MockOrchestrator",
    "MockSpecialist",
    
    # Shared fixtures
    "client_fixture",
    "mock_environment",
    "test_server_fixture"
]
