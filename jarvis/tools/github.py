from __future__ import annotations

"""GitHub integration utilities requiring a Personal Access Token."""

import os
from typing import Optional, Dict, Any, List

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


def list_bug_issues(
    repo: str,
    token: Optional[str] = None,
    state: str = "open",
    since: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return bug-labelled issues from a repository."""
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub token required")

    url = f"https://api.github.com/repos/{repo}/issues"
    params = {"state": state, "labels": "bug"}
    if since:
        params["since"] = since
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return [i for i in response.json() if "pull_request" not in i]


registry.register(
    name="create_issue",
    func=create_issue,
    description="Create a GitHub issue using a Personal Access Token",
    capabilities=["github"],
)

registry.register(
    name="list_bug_issues",
    func=list_bug_issues,
    description="List open GitHub issues labelled as bug",
    capabilities=["github"],
)
