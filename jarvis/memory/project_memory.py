# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""Lightweight project memory management for testing and development.

This module provides a simplified in-memory implementation of project memory
functionality for testing and development purposes. The real project memory
implementation is more complex and depends on external storage systems.

This shim provides a minimal API surface that allows unit tests and development
code to work with the ProjectMemory interface without requiring complex external
dependencies.

Key Features:
- Simple in-memory key-value storage
- List-based entry management per key
- Basic CRUD operations (create, read, clear)
- Thread-safe for single-threaded access
- No external dependencies

Note:
This is a simplified implementation intended for testing and development.
Production use should implement proper persistence and more sophisticated
query capabilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ProjectMemory:
    """Simple in-memory project memory storage for testing.
    
    Provides a lightweight implementation of project memory functionality
    using in-memory dictionaries. This is primarily intended for testing
    and development scenarios where external storage dependencies should
    be avoided.
    
    The class uses a simple key-value store where each key maps to a list
    of entries, allowing multiple items to be stored under the same key.
    
    Example:
        >>> memory = ProjectMemory()
        >>> memory.add_entry("tasks", {"id": 1, "name": "Test task"})
        >>> memory.query("tasks")
        [{"id": 1, "name": "Test task"}]
        
    Attributes:
        _store: Internal storage mapping keys to lists of entries
    """

    def __init__(self) -> None:
        """Initialize the ProjectMemory with empty storage.
        
        Sets up the internal storage dictionary for managing project memory
        entries. No external initialization is required.
        """
        # Simple key -> list of entries storage
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def add_entry(self, key: str, entry: Dict[str, Any]) -> None:
        """Add a new entry to the project memory under the specified key.
        
        Creates a new list for the key if it doesn't exist, then appends
        the entry to the list. This allows multiple entries to be stored
        under the same logical key.
        
        Args:
            key: The storage key for organizing entries
            entry: Dictionary containing the entry data to store
        """
        self._store.setdefault(key, []).append(entry)

    def query(self, key: str) -> List[Dict[str, Any]]:
        """Retrieve all entries stored under the specified key.
        
        Returns a copy of the list of entries for the given key. If no
        entries exist for the key, returns an empty list.
        
        Args:
            key: The storage key to query
            
        Returns:
            List of entries stored under the key, or empty list if none exist
        """
        return list(self._store.get(key, []))

    def clear(self, key: Optional[str] = None) -> None:
        """Clear entries from the project memory.
        
        If key is provided, removes all entries for that specific key.
        If key is None, clears all stored data.
        
        Args:
            key: Optional specific key to clear. If None, clears all data.
        """
        if key is None:
            # Clear all stored data
            self._store.clear()
        else:
            # Remove specific key and all its entries
            self._store.pop(key, None)
