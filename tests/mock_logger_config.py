# Mock logger_config for testing compatibility
"""Mock logger configuration for testing purposes."""

import logging

# Create a simple mock logger
class MockLogger:
    def info(self, msg, *args, **kwargs):
        print(f"INFO: {msg}")
    
    def warning(self, msg, *args, **kwargs):
        print(f"WARNING: {msg}")
    
    def error(self, msg, *args, **kwargs):
        print(f"ERROR: {msg}")
    
    def debug(self, msg, *args, **kwargs):
        print(f"DEBUG: {msg}")

# Create a mock log instance
log = MockLogger()
