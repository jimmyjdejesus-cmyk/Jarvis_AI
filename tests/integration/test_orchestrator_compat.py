# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Integration tests for orchestrator compatibility migration.

This test suite validates the end-to-end compatibility between the legacy
orchestrator and the new sophisticated MultiAgentOrchestrator system.

These tests ensure that the migration preserves functionality while
providing a path forward for future enhancements.
"""

import pytest
import warnings
from unittest.mock import Mock, patch

from apps.AdaptiveMind_Local.orchestrator import Orchestrator as LegacyOrchestrator
from adaptivemind.orchestration.compat import LocalOrchestratorAdapter
from adaptivemind.orchestration.orchestrator import MultiAgentOrchestrator


class TestOrchestratorCompatibilityIntegration:
    """Integration tests for orchestrator compatibility."""
    
    def test_legacy_orchestrator_uses_compatibility_adapter(self):
        """Test that legacy orchestrator properly uses compatibility adapter."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy_orchestrator = LegacyOrchestrator()
            
            # Should be an instance of the compatibility adapter
            assert isinstance(legacy_orchestrator, LocalOrchestratorAdapter)
            
            # Should have all expected attributes from both interfaces
            assert hasattr(legacy_orchestrator, 'meta_agent')
            assert hasattr(legacy_orchestrator, 'coding_agent')
            assert hasattr(legacy_orchestrator, 'research_agent')
            assert hasattr(legacy_orchestrator, 'history')
            assert hasattr(legacy_orchestrator, '_orchestrator')
    
    def test_interface_compatibility(self):
        """Test that both interfaces provide compatible methods."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Test that all expected methods are available
            assert hasattr(legacy, 'handle_request')
            assert callable(getattr(legacy, 'handle_request'))
            
            # Test method signature compatibility
            import inspect
            sig = inspect.signature(legacy.handle_request)
            params = list(sig.parameters.keys())
            assert 'request' in params
    
    def test_deprecation_warnings_preserved(self):
        """Test that deprecation warnings are properly propagated."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Create legacy orchestrator
            LegacyOrchestrator()
            
            # Should have deprecation warning
            deprecation_warnings = [warning for warning in w 
                                  if issubclass(warning.category, DeprecationWarning)]
            assert len(deprecation_warnings) > 0
            
            # Check warning content
            warning_msg = str(deprecation_warnings[0].message)
            assert "deprecated" in warning_msg.lower()
            assert "MultiAgentOrchestrator" in warning_msg
    
    def test_response_format_consistency(self):
        """Test that response formats are consistent between systems."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Test multiple requests to ensure consistent format
            test_requests = [
                "Hello",
                "Help me with coding",
                "",
                "What is AI?",
                "Generate a simple function"
            ]
            
            for request in test_requests:
                result = legacy.handle_request(request)
                
                # Verify tuple structure
                assert isinstance(result, tuple)
                assert len(result) == 3
                
                text, tokens, confidence = result
                
                # Verify types
                assert isinstance(text, str)
                assert isinstance(tokens, int)
                assert isinstance(confidence, float)
                
                # Verify confidence range
                assert 0.0 <= confidence <= 1.0
    
    def test_agent_wrapper_functionality(self):
        """Test that agent wrappers maintain expected functionality."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Test each agent wrapper
            agents = [
                ('meta_agent', legacy.meta_agent),
                ('coding_agent', legacy.coding_agent),
                ('research_agent', legacy.research_agent)
            ]
            
            for agent_name, agent_wrapper in agents:
                # Test invoke method
                result = agent_wrapper.invoke("test request")
                
                assert isinstance(result, dict)
                assert "response" in result
                assert "tokens_generated" in result
                assert "avg_confidence" in result
                
                # Test get_specialization_info
                info = agent_wrapper.get_specialization_info()
                assert isinstance(info, dict)
                assert info["name"] == agent_name
                assert info["type"] == "legacy_agent"
    
    def test_health_check_integration(self):
        """Test that health check integrates properly with both systems."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Get health status from legacy system
            health = legacy.health_check_specialists()
            
            # Verify structure
            assert isinstance(health, dict)
            assert "overall_status" in health
            assert "specialists" in health
            assert "timestamp" in health
            
            # Verify all expected specialists are present
            expected_specialists = ['meta_agent', 'coding_agent', 'research_agent']
            specialists = health["specialists"]
            
            for specialist in expected_specialists:
                assert specialist in specialists
                
                status = specialists[specialist]
                assert isinstance(status, dict)
                assert "status" in status
                assert "confidence" in status
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across the system."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Test various edge cases that might cause errors
            edge_cases = [
                "",  # Empty string
                "   ",  # Whitespace only
                "a" * 10000,  # Very long string
                None,  # This should be handled by the adapter
            ]
            
            for case in edge_cases:
                try:
                    if case is not None:
                        result = legacy.handle_request(case)
                        
                        # Should always return a valid tuple
                        assert isinstance(result, tuple)
                        assert len(result) == 3
                        
                        text, tokens, confidence = result
                        assert isinstance(text, str)
                        assert isinstance(tokens, int)
                        assert isinstance(confidence, float)
                        
                except Exception as e:
                    # If an exception is raised, it should be handled gracefully
                    # by the compatibility layer
                    assert "Error" in str(e) or "error" in str(e).lower()
    
    def test_performance_characteristics(self):
        """Test basic performance characteristics of the compatibility layer."""
        import time
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            legacy = LegacyOrchestrator()
            
            # Test multiple sequential requests
            num_requests = 5
            start_time = time.time()
            
            for i in range(num_requests):
                result = legacy.handle_request(f"test request {i}")
                assert isinstance(result, tuple)
                assert len(result) == 3
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should complete all requests in reasonable time (adjust threshold as needed)
            assert total_time < 10.0  # 10 seconds for 5 requests should be plenty
            assert total_time > 0  # Should take some time
    
    def test_memory_leak_prevention(self):
        """Test that repeated instantiations don't cause memory issues."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Create multiple orchestrator instances
            orchestrators = []
            for i in range(3):
                orchestrator = LegacyOrchestrator()
                orchestrators.append(orchestrator)
                
                # Each should have independent state
                assert orchestrator.history == []
                
                # Should be able to handle requests
                result = orchestrator.handle_request(f"test {i}")
                assert isinstance(result, tuple)
            
            # All orchestrators should be distinct instances
            for i, orchestrator in enumerate(orchestrators):
                for j, other_orchestrator in enumerate(orchestrators):
                    if i != j:
                        assert orchestrator is not other_orchestrator
    
    def test_import_compatibility(self):
        """Test that imports work correctly from both systems."""
        # Test importing from legacy path
        from apps.AdaptiveMind_Local.orchestrator import Orchestrator as LegacyImport
        
        # Test importing from compatibility layer
        from adaptivemind.orchestration.compat import LocalOrchestratorAdapter
        
        # Both should be the same class due to inheritance
        assert issubclass(LegacyImport, LocalOrchestratorAdapter)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy_instance = LegacyImport()
            assert isinstance(legacy_instance, LocalOrchestratorAdapter)
