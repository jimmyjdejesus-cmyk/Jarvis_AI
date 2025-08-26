"""Simple Time-based One-Time Password (TOTP) helper."""

from __future__ import annotations

import pyotp


class TwoFactorAuth:
    """Utility for generating and verifying TOTP codes."""

    def __init__(self, secret: str | None = None):
        self.secret = secret or pyotp.random_base32()

    def provisioning_uri(self, username: str, issuer: str = "JarvisAI") -> str:
        """Return URI for configuring authenticator apps."""
        totp = pyotp.TOTP(self.secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    def verify(self, token: str) -> bool:
        """Validate a user-provided token."""
        totp = pyotp.TOTP(self.secret)
        return totp.verify(token)


__all__ = ["TwoFactorAuth"]