# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Jarvis AI Audit System

A comprehensive audit system for security vulnerabilities, performance bottlenecks,
code quality issues, dependency risks, API compliance, and architectural patterns.
"""

from .models import AuditFinding, AuditReport, ScanConfiguration
from .engine import AuditEngine
from .scanner import SecurityScanner, CodeQualityScanner, DependencyScanner

__version__ = "1.0.0"
__all__ = [
    "AuditFinding",
    "AuditReport", 
    "ScanConfiguration",
    "AuditEngine",
    "SecurityScanner",
    "CodeQualityScanner", 
    "DependencyScanner"
]
