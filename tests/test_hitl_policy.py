import asyncio
import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.hitl.policy import HITLPolicy


def test_async_request_approval():
    async def modal(request):
        return True

    policy = HITLPolicy(config={"hitl": {"destructive_ops": ["file_write"]}})
    assert policy.requires_approval("file_write")
    approved = asyncio.run(
        policy.request_approval("file_write", "test write", modal, user="alice")
    )
    assert approved


def test_request_approval_sync():
    async def modal(request):
        return True

    policy = HITLPolicy(config={"hitl": {"destructive_ops": ["file_delete"]}})
    assert policy.request_approval_sync("file_delete", "test delete", modal, user="bob")
