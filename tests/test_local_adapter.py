# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Unit tests for the local adapter compatibility layer.

This test suite validates the functionality of the compatibility adapter
that provides backward compatibility for the legacy orchestrator.
"""

import pytest
import warnings
from unittest.mock import Mock, MagicMock

from adaptivemind.orchestration.compat import LocalOrchestratorAdapter, LocalAgentWrapper


class TestLocalAgentWrapper:
    """Test suite for the LocalAgentWrapper class."""
    
    def test_wrapper_initialization(self):
        """Test that the wrapper initializes correctly with an agent."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        
        wrapper = LocalAgentWrapper(mock_agent)
        
        assert wrapper._agent == mock_agent
        assert wrapper.name == "test_agent"
    
    def test_wrapper_with_default_name(self):
        """Test that wrapper uses 'unknown' name when agent has no name attribute."""
        mock_agent = Mock()
        del mock_agent.name  # Remove name attribute
        
        wrapper = LocalAgentWrapper(mock_agent)
        
        assert wrapper.name == "unknown"
    
    def test_invoke_with_dict_response(self):
        """Test invoke method with dictionary response."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.invoke.return_value = {
            "response": "test response",
            "tokens_generated": 10,
            "avg_confidence": 0.8
        }
        
        wrapper = LocalAgentWrapper(mock_agent)
        result = wrapper.invoke("test request")
        
        assert result == {
            "response": "test response",
            "tokens_generated": 10,
            "avg_confidence": 0.8
        }
        mock_agent.invoke.assert_called_once_with("test request")
    
    def test_invoke_with_non_dict_response(self):
        """Test invoke method with non-dictionary response."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.invoke.return_value = "simple string response"
        
        wrapper = LocalAgentWrapper(mock_agent)
        result = wrapper.invoke("test request")
        
        assert result["response"] == "simple string response"
        assert result["tokens_generated"] == 0
        assert result["avg_confidence"] == 0.7
    
    def test_invoke_without_invoke_method(self):
        """Test invoke method when agent doesn't have invoke method."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        del mock_agent.invoke  # Remove invoke method
        
        wrapper = LocalAgentWrapper(mock_agent)
        result = wrapper.invoke("test request")
        
        assert result["response"] == "Agent test_agent processed: test request"
        assert result["tokens_generated"] == 10
        assert result["avg_confidence"] == 0.8
    
    def test_invoke_with_exception(self):
        """Test invoke method handles exceptions gracefully."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.invoke.side_effect = Exception("Test error")
        
        wrapper = LocalAgentWrapper(mock_agent)
        result = wrapper.invoke("test request")
        
        assert "Error processing request" in result["response"]
        assert result["tokens_generated"] == 0
        assert result["avg_confidence"] == 0.0
    
    def test_get_specialization_info(self):
        """Test get_specialization_info method."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        
        wrapper = LocalAgentWrapper(mock_agent)
        info = wrapper.get_specialization_info()
        
        expected = {
            "name": "test_agent",
            "type": "legacy_agent",
            "status": "active",
            "capabilities": ["compatibility_wrapper"]
        }
        
        assert info == expected


class TestLocalOrchestratorAdapter:
    """Test suite for the LocalOrchestratorAdapter class."""
    
    def test_adapter_initialization(self):
        """Test that the adapter initializes correctly."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        # Check that the underlying orchestrator is created
        assert hasattr(adapter, '_orchestrator')
        
        # Check that legacy agent wrappers are created
        assert hasattr(adapter, 'meta_agent')
        assert hasattr(adapter, 'coding_agent')
        assert hasattr(adapter, 'research_agent')
        
        # Check legacy attributes
        assert hasattr(adapter, 'history')
        assert adapter.history == []
        
        # Check agent mapping
        assert hasattr(adapter, '_agent_map')
        assert 'meta_agent' in adapter._agent_map
        assert 'coding_agent' in adapter._agent_map
        assert 'research_agent' in adapter._agent_map
    
    def test_adapter_deprecation_warning(self):
        """Test that adapter initialization produces deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            adapter = LocalOrchestratorAdapter()
            
            # Check that a deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "MultiAgentOrchestrator" in str(w[0].message)
    
    def test_handle_request_success(self):
        """Test handle_request method with successful response."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        result = adapter.handle_request("test request")
        
        # Check return type and structure
        assert isinstance(result, tuple)
        assert len(result) == 3
        text, tokens, confidence = result
        
        assert isinstance(text, str)
        assert isinstance(tokens, int)
        assert isinstance(confidence, float)
    
    def test_handle_request_error_handling(self):
        """Test handle_request method with error handling."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        # Test with empty request
        result = adapter.handle_request("")
        
        # Should still return valid tuple
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_get_specialist_registry(self):
        """Test get_specialist_registry method."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        registry = adapter.get_specialist_registry()
        assert isinstance(registry, dict)
    
    def test_health_check_specialists(self):
        """Test health_check_specialists method."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        health = adapter.health_check_specialists()
        
        # Check structure
        assert isinstance(health, dict)
        assert "overall_status" in health
        assert "specialists" in health
        assert "timestamp" in health
        
        # Check specialists
        specialists = health["specialists"]
        assert isinstance(specialists, dict)
        assert "meta_agent" in specialists
        assert "coding_agent" in specialists
        assert "research_agent" in specialists
        
        # Check individual specialist status
        for specialist_status in specialists.values():
            assert isinstance(specialist_status, dict)
            assert "status" in specialist_status
            assert "confidence" in specialist_status
    
    def test_agent_wrappers_have_invoke_method(self):
        """Test that agent wrappers have the invoke method."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        assert hasattr(adapter.meta_agent, 'invoke')
        assert hasattr(adapter.coding_agent, 'invoke')
        assert hasattr(adapter.research_agent, 'invoke')
    
    def test_agent_wrapper_invocation(self):
        """Test that agent wrappers can be invoked."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            adapter = LocalOrchestratorAdapter()
        
        # Test meta agent invocation
        result = adapter.meta_agent.invoke("test")
        assert isinstance(result, dict)
        assert "response" in result
        assert "tokens_generated" in result
        assert "avg_confidence" in result
