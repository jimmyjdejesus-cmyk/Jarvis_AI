from __future__ import annotations

"""GitHub integration utilities requiring a Personal Access Token."""

import os
from typing import Optional, Dict, Any

import requests

from .registry import registry


def create_issue(
    repo: str,
    title: str,
    body: str,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an issue on GitHub using a PAT.

    Parameters
    ----------
    repo: str
        Repository in ``owner/name`` form.
    title: str
        Issue title.
    body: str
        Issue body text.
    token: Optional[str]
        Personal Access Token. Falls back to ``GITHUB_TOKEN`` environment
        variable if not provided.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub token required")

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(url, json={"title": title, "body": body}, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


registry.register(
    name="create_issue",
    func=create_issue,
    description="Create a GitHub issue using a Personal Access Token",
    capabilities=["github"],
)
