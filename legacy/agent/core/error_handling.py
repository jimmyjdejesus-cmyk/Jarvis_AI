"""
Enhanced Error Handling and Logging System for Jarvis AI
Provides comprehensive error handling, logging, and diagnostic capabilities.
"""

import logging
import traceback
import sys
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from functools import wraps
import json


class JarvisLogger:
    """Enhanced logging system for Jarvis AI with multiple output formats."""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = log_level.upper()
        self.log_file = log_file or "logs/jarvis.log"
        self.setup_logger()
    
    def setup_logger(self):
        """Setup comprehensive logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("jarvis_ai")
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colorized output
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logging
        file_handler = logging.FileHandler(self.log_file)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with full context and traceback."""
        context = context or {}
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(f"ERROR: {error_info['error_type']}: {error_info['error_message']}")
        self.logger.debug(f"Full error context: {json.dumps(error_info, indent=2)}")
        
        return error_info
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics."""
        perf_info = {
            "operation": operation,
            "duration_seconds": duration,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        if duration > 5.0:  # Log slow operations
            self.logger.warning(f"SLOW OPERATION: {operation} took {duration:.2f}s")
        else:
            self.logger.info(f"PERFORMANCE: {operation} completed in {duration:.2f}s")
        
        self.logger.debug(f"Performance details: {json.dumps(perf_info, indent=2)}")


class ErrorHandler:
    """Comprehensive error handling with recovery strategies."""
    
    def __init__(self, logger: JarvisLogger):
        self.logger = logger
        self.error_count = {}
        self.recovery_strategies = {}
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """Register a recovery strategy for specific error types."""
        self.recovery_strategies[error_type] = strategy
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    operation: str = "unknown") -> Dict[str, Any]:
        """Handle error with logging and recovery attempts."""
        error_type = type(error)
        
        # Track error frequency
        self.error_count[error_type] = self.error_count.get(error_type, 0) + 1
        
        # Log the error
        error_info = self.logger.log_error(error, context)
        error_info["operation"] = operation
        error_info["error_count"] = self.error_count[error_type]
        
        # Attempt recovery if strategy exists
        if error_type in self.recovery_strategies:
            try:
                recovery_result = self.recovery_strategies[error_type](error, context)
                error_info["recovery_attempted"] = True
                error_info["recovery_result"] = recovery_result
                self.logger.logger.info(f"Recovery attempted for {error_type.__name__}")
            except Exception as recovery_error:
                error_info["recovery_failed"] = str(recovery_error)
                self.logger.log_error(recovery_error, {"original_error": str(error)})
        
        return error_info
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "total_errors": sum(self.error_count.values()),
            "error_breakdown": {err_type.__name__: count 
                             for err_type, count in self.error_count.items()},
            "timestamp": datetime.now().isoformat()
        }


def robust_operation(logger: JarvisLogger = None, 
                    error_handler: ErrorHandler = None,
                    max_retries: int = 3,
                    operation_name: str = None):
    """Decorator for making operations robust with error handling and retries."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger, error_handler, operation_name
            
            if logger is None:
                logger = JarvisLogger()
            if error_handler is None:
                error_handler = ErrorHandler(logger)
            if operation_name is None:
                operation_name = f"{func.__module__}.{func.__name__}"
            
            start_time = datetime.now()
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful operation
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.log_performance(operation_name, duration, 
                                         {"attempt": attempt + 1, "success": True})
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    context = {
                        "function": func.__name__,
                        "args": str(args)[:200],  # Truncate to avoid huge logs
                        "kwargs": str(kwargs)[:200],
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    }
                    
                    error_info = error_handler.handle_error(e, context, operation_name)
                    
                    if attempt < max_retries:
                        logger.logger.warning(f"Retrying {operation_name} (attempt {attempt + 2}/{max_retries + 1})")
                        continue
                    else:
                        logger.logger.error(f"Operation {operation_name} failed after {max_retries + 1} attempts")
                        raise e
            
            # This should never be reached, but just in case
            raise last_error if last_error else Exception("Unknown error in robust operation")
        
        return wrapper
    return decorator


class SystemHealthChecker:
    """System health monitoring and diagnostics."""
    
    def __init__(self, logger: JarvisLogger):
        self.logger = logger
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if all required dependencies are available."""
        dependencies = {
            "ollama": self._check_ollama(),
            "git": self._check_git(),
            "python_modules": self._check_python_modules()
        }
        
        self.logger.logger.info(f"Dependency check completed: {dependencies}")
        return dependencies
    
    def _check_ollama(self) -> Dict[str, Any]:
        """Check if Ollama is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return {"available": True, "status_code": response.status_code}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_git(self) -> Dict[str, Any]:
        """Check if git is available."""
        try:
            import subprocess
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            return {"available": True, "version": result.stdout.strip()}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_python_modules(self) -> Dict[str, Any]:
        """Check if required Python modules are available."""
        required_modules = [
            "streamlit", "requests", "cryptography", "bcrypt", 
            "playwright", "duckduckgo_search", "plotly", "psutil"
        ]
        
        module_status = {}
        for module in required_modules:
            try:
                __import__(module)
                module_status[module] = {"available": True}
            except ImportError as e:
                module_status[module] = {"available": False, "error": str(e)}
        
        return module_status
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            import psutil
            import platform
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


# Global instances for easy access
_global_logger = None
_global_error_handler = None
_global_health_checker = None


def get_logger() -> JarvisLogger:
    """Get global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = JarvisLogger()
    return _global_logger


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(get_logger())
    return _global_error_handler


def get_health_checker() -> SystemHealthChecker:
    """Get global health checker instance."""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = SystemHealthChecker(get_logger())
    return _global_health_checker


# Recovery strategies for common errors
def register_common_recovery_strategies():
    """Register common recovery strategies."""
    error_handler = get_error_handler()
    
    def import_error_recovery(error: ImportError, context: Dict[str, Any]):
        """Suggest installation of missing modules."""
        missing_module = str(error).split("'")[1] if "'" in str(error) else "unknown"
        return f"Try installing missing module: pip install {missing_module}"
    
    def connection_error_recovery(error: Exception, context: Dict[str, Any]):
        """Suggest checking network connectivity."""
        return "Check network connectivity and service availability"
    
    error_handler.register_recovery_strategy(ImportError, import_error_recovery)
    error_handler.register_recovery_strategy(ConnectionError, connection_error_recovery)


# Initialize common recovery strategies
register_common_recovery_strategies()