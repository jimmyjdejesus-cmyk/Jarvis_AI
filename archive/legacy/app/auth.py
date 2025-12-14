from __future__ import annotations

from typing import Callable, Any
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def login_for_access_token() -> Callable[[Any], Token]:
    """Minimal auth helper used by legacy app tests.

    Returns a callable that produces a `Token`. For testing we just return
    a no-op implementation that yields a dummy token.
    """
    def _login(*args, **kwargs):
        return Token(access_token="test-token")

    return _login


def role_required(role: str):
    """Decorator that enforces a role — tests only need a no-op decorator.
    """
    def _decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return _decorator
