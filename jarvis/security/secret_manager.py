# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from __future__ import annotations
from typing import Any, Dict

_secrets_store: Dict[str, Any] = {}

def set_secret(key: str, value: str) -> bool:
    _secrets_store[key] = value
    return True

def get_secret(key: str, default: Any = None) -> Any:
    return _secrets_store.get(key, default)
