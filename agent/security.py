"""Security features for Jarvis AI."""

from pathlib import Path

try:
    from agent.features.security import *  # type: ignore  # noqa: F401,F403
except ImportError:
    # Fallback implementations with basic security features
    import bcrypt
    from datetime import datetime, timedelta
    import logging
    from typing import Dict, List, Optional

    logger = logging.getLogger(__name__)
    _rate_limit_storage: Dict[str, List[datetime]] = {}

    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8"),
            )
        except Exception:
            logger.exception("Password verification failed")
            return False

    def is_rate_limited(
        identifier: str, max_attempts: int = 5, window_minutes: int = 15
    ) -> bool:
        """Return True if identifier exceeded max attempts in window."""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        attempts = _rate_limit_storage.setdefault(identifier, [])
        # prune old attempts
        _rate_limit_storage[identifier] = [
            ts for ts in attempts if ts > window_start
        ]  # noqa: E501
        if len(_rate_limit_storage[identifier]) >= max_attempts:
            return True
        _rate_limit_storage[identifier].append(now)
        return False

    def log_security_event(
        event_type: str,
        username: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log security events for auditing."""
        logger.info(
            "Security Event: %s - User: %s - Details: %s",
            event_type,
            username,
            details,
        )

    def validate_password_strength(password: str) -> bool:
        """Validate password strength using basic complexity rules."""
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        return all([has_upper, has_lower, has_digit, has_special])

    def load_user_key(username: str) -> None:
        """Placeholder for loading a user encryption key."""
        return None

    def encrypt_json(data, key):
        """Encrypt JSON data (placeholder)."""
        return data

    def decrypt_json(data, key):
        """Decrypt JSON data (placeholder)."""
        return data

    def is_safe_path(base: Path, path: Path) -> bool:
        """Return True if ``path`` is within ``base`` to prevent traversal."""
        base = base.resolve()
        if not path.is_absolute():
            path = (base / path).resolve()
        else:
            path = path.resolve()
        return base == path or base in path.parents
