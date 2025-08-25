"""Validation tests for custom web tools."""

import sys
import types
from pathlib import Path

import pytest

# Ensure the integrations package resolves to the local directory
root = Path(__file__).resolve().parents[1]
integrations_pkg = types.ModuleType("integrations")
integrations_pkg.__path__ = [str(root / "integrations")]
sys.modules.setdefault("integrations", integrations_pkg)

from integrations.custom_tools import WebScraperTool, NotificationTool


def test_web_scraper_rejects_invalid_url() -> None:
    tool = WebScraperTool()
    with pytest.raises(ValueError):
        tool.execute("javascript:alert(1)")


def test_webhook_notification_rejects_invalid_url() -> None:
    tool = NotificationTool()
    with pytest.raises(ValueError):
        tool.execute("hello", channel="webhook", webhook_url="ftp://bad")
