import sys
from pathlib import Path
import asyncio
import pytest

# Combine imports from both versions
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.hitl.policy import HITLPolicy


# Keep the test from your feature branch
def test_requires_approval_and_audit():
    policy = HITLPolicy()
    assert policy.requires_approval("git_write")
    assert not policy.requires_approval("read")

    def modal(request):
        assert request.action == "git_write"
        return True

    approved = policy.request_approval(
        "git_write",
        "testing",
        modal,
        user="tester",
    )
    assert approved
    assert policy.audit and policy.audit[-1].approved
    assert policy.audit[-1].user == "tester"


# Keep the tests from the main branch
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