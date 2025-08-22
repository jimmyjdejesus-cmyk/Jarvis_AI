"""HTTP client for interacting with the shared memory service."""

from __future__ import annotations

from typing import Iterable, Optional, Protocol, Set

import requests


class HttpClient(Protocol):
    def post(self, url: str, json: dict, timeout: int) -> any:  # pragma: no cover - protocol
        ...

    def get(self, url: str, timeout: int) -> any:  # pragma: no cover - protocol
        ...


class ACLViolation(Exception):
    """Raised when a principal attempts to access a forbidden scope."""


class MemoryClient:
    """Client enforcing principal-based ACL for memory operations."""

    def __init__(
        self,
        base_url: str,
        principal: str,
        allowed_scopes: Iterable[str],
        http_client: Optional[HttpClient] = None,
    ) -> None:
        if base_url.startswith("file://"):
            raise ValueError("Filesystem access is prohibited")
        self.base_url = base_url.rstrip("/")
        self.principal = principal
        self.allowed_scopes: Set[str] = set(allowed_scopes)
        self.http: HttpClient = http_client or requests

    # ------------------------------------------------------------------
    def _check_scope(self, scope: str) -> None:
        if scope not in self.allowed_scopes:
            raise ACLViolation(
                f"Scope '{scope}' not permitted for principal '{self.principal}'."
            )

    def write(self, scope: str, key: str, value: str) -> None:
        self._check_scope(scope)
        url = f"{self.base_url}/{self.principal}/{scope}"
        payload = {"key": key, "value": value}
        headers = {"X-Principal": self.principal}
        response = self.http.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()

    def read(self, scope: str, key: str) -> str:
        self._check_scope(scope)
        url = f"{self.base_url}/{self.principal}/{scope}/{key}"
        headers = {"X-Principal": self.principal}
        response = self.http.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["value"]

    def scope_hash(self, scope: str) -> str:
        self._check_scope(scope)
        url = f"{self.base_url}/{self.principal}/{scope}/hash"
        headers = {"X-Principal": self.principal}
        response = self.http.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["hash"]
