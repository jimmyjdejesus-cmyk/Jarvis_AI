# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Integration tests for legacy orchestrator behavior compatibility.

This test suite validates that the legacy `apps.AdaptiveMind_Local.Orchestrator`
maintains the same behavior after migration to the compatibility layer.

These tests ensure backward compatibility during the migration period.
"""

import pytest
import warnings
from unittest.mock import Mock, patch

# Import the compatibility orchestrator
from apps.AdaptiveMind_Local.orchestrator import Orchestrator


class TestLocalOrchestratorCompatibility:
    """Test suite for legacy orchestrator compatibility."""
    
    def test_orchestrator_initialization(self):
        """Test that the orchestrator initializes correctly."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Check that all expected attributes are present
            assert hasattr(orchestrator, 'meta_agent')
            assert hasattr(orchestrator, 'coding_agent')
            assert hasattr(orchestrator, 'research_agent')
            assert hasattr(orchestrator, 'history')
            assert orchestrator.history == []
    
    def test_orchestrator_deprecation_warning(self):
        """Test that using the legacy orchestrator produces a deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            orchestrator = Orchestrator()
            
            # Check that a deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "MultiAgentOrchestrator" in str(w[0].message)
    
    def test_handle_request_returns_tuple(self):
        """Test that handle_request returns the expected tuple format."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            result = orchestrator.handle_request("test request")
            
            # Check return type and structure
            assert isinstance(result, tuple)
            assert len(result) == 3
            text, tokens, confidence = result
            
            assert isinstance(text, str)
            assert isinstance(tokens, int)
            assert isinstance(confidence, float)
    
    def test_handle_request_content_format(self):
        """Test that handle_request returns content in expected format."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            result = orchestrator.handle_request("test request")
            text, tokens, confidence = result
            
            # Basic validation of response format
            assert len(text) > 0  # Should have some response text
            assert tokens >= 0  # Tokens should be non-negative
            assert 0.0 <= confidence <= 1.0  # Confidence should be in valid range
    
    def test_orchestrator_has_expected_methods(self):
        """Test that the orchestrator has all expected public methods."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Check for expected methods
            assert hasattr(orchestrator, 'handle_request')
            assert hasattr(orchestrator, 'get_specialist_registry')
            assert hasattr(orchestrator, 'health_check_specialists')
    
    def test_agents_have_invoke_method(self):
        """Test that agent wrappers have the invoke method."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Check that all agents have invoke method
            assert hasattr(orchestrator.meta_agent, 'invoke')
            assert hasattr(orchestrator.coding_agent, 'invoke')
            assert hasattr(orchestrator.research_agent, 'invoke')
    
    def test_agent_invoke_returns_dict(self):
        """Test that agent invoke method returns a dictionary."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Test meta agent
            result = orchestrator.meta_agent.invoke("test")
            assert isinstance(result, dict)
            assert "response" in result
            assert "tokens_generated" in result
            assert "avg_confidence" in result
    
    def test_error_handling(self):
        """Test that the orchestrator handles errors gracefully."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Test with an empty request
            result = orchestrator.handle_request("")
            text, tokens, confidence = result
            
            # Should still return valid tuple even with empty input
            assert isinstance(result, tuple)
            assert len(result) == 3
            assert isinstance(text, str)
            assert isinstance(tokens, int)
            assert isinstance(confidence, float)
    
    def test_specialist_registry_access(self):
        """Test that specialist registry can be accessed."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            registry = orchestrator.get_specialist_registry()
            assert isinstance(registry, dict)
    
    def test_health_check(self):
        """Test that health check returns expected format."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            health = orchestrator.health_check_specialists()
            
            # Check structure
            assert isinstance(health, dict)
            assert "overall_status" in health
            assert "specialists" in health
            assert "timestamp" in health
            
            # Check specialists structure
            specialists = health["specialists"]
            assert isinstance(specialists, dict)
            assert "meta_agent" in specialists
            assert "coding_agent" in specialists
            assert "research_agent" in specialists
            
            # Check individual specialist status
            for specialist_name, status in specialists.items():
                assert isinstance(status, dict)
                assert "status" in status
                assert "confidence" in status
    
    @patch('warnings.warn')
    def test_inheritance_from_compatibility_adapter(self, mock_warn):
        """Test that orchestrator properly inherits from compatibility adapter."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            orchestrator = Orchestrator()
            
            # Should be an instance of the compatibility adapter
            from adaptivemind.orchestration.compat import LocalOrchestratorAdapter
            assert isinstance(orchestrator, LocalOrchestratorAdapter)
    
    def test_backward_compatibility_preserved(self):
        """Test that all legacy behavior is preserved."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Test multiple instantiations
            orchestrator1 = Orchestrator()
            orchestrator2 = Orchestrator()
            
            # Each should have independent state
            assert orchestrator1 is not orchestrator2
            assert orchestrator1.history == []
            assert orchestrator2.history == []
            
            # Test method calls
            result1 = orchestrator1.handle_request("request1")
            result2 = orchestrator2.handle_request("request2")
            
            assert isinstance(result1, tuple)
            assert isinstance(result2, tuple)
            assert len(result1) == 3
            assert len(result2) == 3
