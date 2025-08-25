import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.hitl.policy import HITLPolicy  # noqa: E402


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
