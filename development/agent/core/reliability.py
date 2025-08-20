"""
Enhanced Reliability and Fallback System for Jarvis AI V2
Extends existing error handling with graceful degradation and operation modes.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
import os
import sys
from pathlib import Path

# Add legacy path for imports
legacy_path = Path(__file__).parent.parent.parent.parent / "legacy"
sys.path.insert(0, str(legacy_path))

try:
    from agent.core.error_handling import ErrorHandler, JarvisLogger, SystemHealthChecker, get_logger
    from agent.features.rag_handler import get_rag_cache
    from scripts.ollama_client import get_available_models, OLLAMA_ENDPOINT
    LEGACY_AVAILABLE = True
except ImportError as e:
    print(f"Legacy modules not available: {e}")
    LEGACY_AVAILABLE = False

# Try to import Lang ecosystem components
try:
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class OperationMode(Enum):
    """Different operation modes for the system."""
    FULL = "full"  # All features available
    LOCAL_ONLY = "local_only"  # No web RAG, local processing only
    OFFLINE = "offline"  # Cached knowledge only, no external connections
    BASIC = "basic"  # Minimal functionality for low-resource environments
    EMERGENCY = "emergency"  # Critical systems only


class SystemState(Enum):
    """Current system health state."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


class ReliabilityManager:
    """Central manager for system reliability and fallback mechanisms."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.current_mode = OperationMode.FULL
        self.current_state = SystemState.HEALTHY
        self.fallback_history = []
        self.monitoring_enabled = self.config.get("monitoring_enabled", False)  # Disabled by default for testing
        
        # Initialize components
        if LEGACY_AVAILABLE:
            self.logger = get_logger()
            self.error_handler = ErrorHandler(self.logger)
            self.health_checker = SystemHealthChecker(self.logger)
            self.rag_cache = get_rag_cache()
        else:
            # Fallback logger
            import logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("reliability")
            # Create a wrapper to match JarvisLogger interface
            self.logger.logger = self.logger
            self.error_handler = None
            self.health_checker = None
            self.rag_cache = None
        
        # Service status tracking
        self.service_status = {
            "ollama": {"healthy": False, "last_check": None},
            "rag": {"healthy": False, "last_check": None},
            "cache": {"healthy": False, "last_check": None}
        }
        
        # Recovery strategies
        self.recovery_strategies = {
            "ollama_down": self._recover_ollama_service,
            "rag_failure": self._recover_rag_service,
            "cache_corruption": self._recover_cache_service,
            "model_error": self._recover_model_error,
            "network_failure": self._handle_network_failure
        }
        
        # Initialize monitoring (disabled for testing by default)
        if self.monitoring_enabled:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background monitoring of system health."""
        if not self.monitoring_enabled:
            return
        
        # In a production system, this would be a proper background task
        # For now, we'll implement immediate health checks
        self._check_system_health()
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_state": "unknown",
            "services": {},
            "recommendations": []
        }
        
        try:
            # Check Ollama service
            ollama_status = self._check_ollama_health()
            health_report["services"]["ollama"] = ollama_status
            
            # Check RAG system
            rag_status = self._check_rag_health()
            health_report["services"]["rag"] = rag_status
            
            # Check cache system
            cache_status = self._check_cache_health()
            health_report["services"]["cache"] = cache_status
            
            # Determine overall state
            service_health = [ollama_status["healthy"], rag_status["healthy"], cache_status["healthy"]]
            
            if all(service_health):
                health_report["overall_state"] = "healthy"
                self.current_state = SystemState.HEALTHY
                if self.current_mode != OperationMode.FULL:
                    # Consider upgrading mode
                    self._attempt_mode_upgrade()
            elif any(service_health):
                health_report["overall_state"] = "degraded" 
                self.current_state = SystemState.DEGRADED
                self._handle_degraded_state(health_report)
            else:
                health_report["overall_state"] = "critical"
                self.current_state = SystemState.CRITICAL
                self._handle_critical_state(health_report)
                
        except Exception as e:
            health_report["error"] = str(e)
            health_report["overall_state"] = "error"
            if self.logger:
                self.logger.logger.error(f"Health check failed: {e}")
        
        return health_report
    
    def _check_ollama_health(self) -> Dict[str, Any]:
        """Check Ollama service health."""
        status = {"healthy": False, "error": None, "models": [], "last_check": datetime.now().isoformat()}
        
        try:
            import requests
            response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                status["healthy"] = True
                status["models"] = [model.get("name", "unknown") for model in models_data.get("models", [])]
            else:
                status["error"] = f"HTTP {response.status_code}"
        except Exception as e:
            status["error"] = str(e)
        
        self.service_status["ollama"] = status
        return status
    
    def _check_rag_health(self) -> Dict[str, Any]:
        """Check RAG system health."""
        status = {"healthy": False, "error": None, "cache_size": 0, "last_check": datetime.now().isoformat()}
        
        try:
            if self.rag_cache:
                status["healthy"] = True
                status["cache_size"] = len(getattr(self.rag_cache, 'cache', {}))
            else:
                status["error"] = "RAG cache not available"
        except Exception as e:
            status["error"] = str(e)
        
        self.service_status["rag"] = status
        return status
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        status = {"healthy": True, "error": None, "last_check": datetime.now().isoformat()}
        
        try:
            # Basic cache functionality test
            if self.rag_cache:
                # Test cache write/read
                test_key = f"health_check_{int(time.time())}"
                self.rag_cache.set("test", ["file1"], "test", "test_result")
                result = self.rag_cache.get("test", ["file1"], "test")
                status["healthy"] = result is not None
            else:
                status["error"] = "Cache system not available"
        except Exception as e:
            status["error"] = str(e)
            status["healthy"] = False
        
        self.service_status["cache"] = status
        return status
    
    def _handle_degraded_state(self, health_report: Dict[str, Any]):
        """Handle system degradation by adjusting operation mode."""
        if not health_report["services"]["ollama"]["healthy"]:
            # Ollama is down, switch to cache-only mode
            self._switch_operation_mode(OperationMode.OFFLINE, "Ollama service unavailable")
        elif not health_report["services"]["rag"]["healthy"]:
            # RAG issues, switch to local-only
            self._switch_operation_mode(OperationMode.LOCAL_ONLY, "RAG system degraded")
        else:
            # Other issues, reduce to basic mode
            self._switch_operation_mode(OperationMode.BASIC, "System performance degraded")
    
    def _handle_critical_state(self, health_report: Dict[str, Any]):
        """Handle critical system state."""
        self._switch_operation_mode(OperationMode.EMERGENCY, "Critical system failures detected")
        
        # Attempt recovery for critical services
        for service, status in health_report["services"].items():
            if not status["healthy"] and service in self.recovery_strategies:
                try:
                    recovery_key = f"{service}_failure" if service != "ollama" else "ollama_down"
                    if recovery_key in self.recovery_strategies:
                        self.recovery_strategies[recovery_key]()
                except Exception as e:
                    if self.logger:
                        self.logger.logger.error(f"Recovery failed for {service}: {e}")
    
    def _switch_operation_mode(self, new_mode: OperationMode, reason: str):
        """Switch to a different operation mode."""
        if new_mode == self.current_mode:
            return
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        fallback_event = {
            "timestamp": datetime.now().isoformat(),
            "from_mode": old_mode.value,
            "to_mode": new_mode.value,
            "reason": reason
        }
        
        self.fallback_history.append(fallback_event)
        
        if self.logger:
            self.logger.logger.warning(f"Operation mode switched: {old_mode.value} -> {new_mode.value} ({reason})")
        
        # Apply mode-specific configurations
        self._apply_mode_configuration(new_mode)
    
    def _apply_mode_configuration(self, mode: OperationMode):
        """Apply configuration for the specified operation mode."""
        configurations = {
            OperationMode.FULL: {
                "web_rag_enabled": True,
                "cache_only": False,
                "minimal_features": False,
                "emergency_only": False
            },
            OperationMode.LOCAL_ONLY: {
                "web_rag_enabled": False,
                "cache_only": False,
                "minimal_features": False,
                "emergency_only": False
            },
            OperationMode.OFFLINE: {
                "web_rag_enabled": False,
                "cache_only": True,
                "minimal_features": False,
                "emergency_only": False
            },
            OperationMode.BASIC: {
                "web_rag_enabled": False,
                "cache_only": True,
                "minimal_features": True,
                "emergency_only": False
            },
            OperationMode.EMERGENCY: {
                "web_rag_enabled": False,
                "cache_only": True,
                "minimal_features": True,
                "emergency_only": True
            }
        }
        
        if mode in configurations:
            self.config.update(configurations[mode])
    
    def _attempt_mode_upgrade(self):
        """Attempt to upgrade operation mode when services recover."""
        if self.current_mode == OperationMode.FULL:
            return
        
        # Check if we can upgrade
        health_report = self._check_system_health()
        
        if health_report["overall_state"] == "healthy":
            self._switch_operation_mode(OperationMode.FULL, "All services recovered")
        elif health_report["overall_state"] == "degraded":
            # Upgrade to best available mode
            if health_report["services"]["ollama"]["healthy"]:
                if self.current_mode in [OperationMode.OFFLINE, OperationMode.EMERGENCY]:
                    self._switch_operation_mode(OperationMode.LOCAL_ONLY, "Ollama service recovered")
    
    # Recovery strategy implementations
    def _recover_ollama_service(self):
        """Attempt to recover Ollama service."""
        if self.logger:
            self.logger.logger.info("Attempting Ollama service recovery...")
        
        # In a real implementation, this might restart the service
        # For now, we'll just check if it's back up
        status = self._check_ollama_health()
        return status["healthy"]
    
    def _recover_rag_service(self):
        """Attempt to recover RAG service."""
        if self.logger:
            self.logger.logger.info("Attempting RAG service recovery...")
        
        # Try to reinitialize RAG cache
        try:
            if LEGACY_AVAILABLE:
                from agent.features.rag_handler import get_rag_cache
                self.rag_cache = get_rag_cache()
                return True
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"RAG recovery failed: {e}")
        
        return False
    
    def _recover_cache_service(self):
        """Attempt to recover cache service."""
        if self.logger:
            self.logger.logger.info("Attempting cache service recovery...")
        
        # Clear potentially corrupted cache and reinitialize
        try:
            if self.rag_cache and hasattr(self.rag_cache, 'cache'):
                self.rag_cache.cache.clear()
                return True
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Cache recovery failed: {e}")
        
        return False
    
    def _recover_model_error(self):
        """Attempt to recover from model errors."""
        if self.logger:
            self.logger.logger.info("Attempting model error recovery...")
        
        # Try to reload models or clear model cache
        try:
            if LEGACY_AVAILABLE:
                from scripts.ollama_client import clear_model_cache
                clear_model_cache()
                return True
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Model recovery failed: {e}")
        
        return False
    
    def _handle_network_failure(self):
        """Handle network failure by switching to offline mode."""
        self._switch_operation_mode(OperationMode.OFFLINE, "Network connectivity lost")
        return True
    
    # Public interface methods
    def get_current_mode(self) -> OperationMode:
        """Get current operation mode."""
        return self.current_mode
    
    def get_current_state(self) -> SystemState:
        """Get current system state."""
        return self.current_state
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "mode": self.current_mode.value,
            "state": self.current_state.value,
            "services": self.service_status,
            "fallback_history": self.fallback_history[-10:],  # Last 10 events
            "last_health_check": datetime.now().isoformat()
        }
    
    def force_mode_switch(self, mode: OperationMode, reason: str = "Manual override"):
        """Force switch to a specific operation mode."""
        self._switch_operation_mode(mode, reason)
    
    def can_use_web_rag(self) -> bool:
        """Check if web RAG is available in current mode."""
        return self.config.get("web_rag_enabled", False)
    
    def should_use_cache_only(self) -> bool:
        """Check if system should use cache only."""
        return self.config.get("cache_only", False)
    
    def is_minimal_mode(self) -> bool:
        """Check if system is in minimal feature mode."""
        return self.config.get("minimal_features", False)
    
    def is_emergency_mode(self) -> bool:
        """Check if system is in emergency mode."""
        return self.config.get("emergency_only", False)


# Global reliability manager instance
_reliability_manager = None


def get_reliability_manager(config: Optional[Dict[str, Any]] = None) -> ReliabilityManager:
    """Get global reliability manager instance."""
    global _reliability_manager
    if _reliability_manager is None:
        _reliability_manager = ReliabilityManager(config)
    return _reliability_manager


def with_fallback(fallback_result: Any = None, fallback_mode: Optional[OperationMode] = None):
    """Decorator to add fallback behavior to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            reliability_manager = get_reliability_manager()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error
                if reliability_manager.logger:
                    reliability_manager.logger.logger.error(f"Function {func.__name__} failed: {e}")
                
                # Switch mode if specified
                if fallback_mode:
                    reliability_manager.force_mode_switch(fallback_mode, f"Function {func.__name__} failure")
                
                # Return fallback result
                if callable(fallback_result):
                    return fallback_result(*args, **kwargs)
                else:
                    return fallback_result
        
        return wrapper
    return decorator


# Create LangChain fallback chain if available
if LANGCHAIN_AVAILABLE:
    def create_fallback_chain(primary_func: Callable, fallback_func: Callable):
        """Create a LangChain fallback chain."""
        
        def fallback_logic(inputs):
            try:
                return primary_func(inputs)
            except Exception as e:
                print(f"Primary function failed: {e}, using fallback")
                return fallback_func(inputs)
        
        return RunnableLambda(fallback_logic)
else:
    def create_fallback_chain(primary_func: Callable, fallback_func: Callable):
        """Fallback implementation when LangChain is not available."""
        def fallback_wrapper(*args, **kwargs):
            try:
                return primary_func(*args, **kwargs)
            except Exception as e:
                print(f"Primary function failed: {e}, using fallback")
                return fallback_func(*args, **kwargs)
        return fallback_wrapper