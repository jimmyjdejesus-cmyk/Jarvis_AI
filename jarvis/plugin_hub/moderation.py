"""Moderation utilities for community plugin submissions."""

from typing import Dict, List
from uuid import uuid4
from fastapi import Depends, HTTPException

from .auth import require_role

# In-memory queue of pending submissions {id: data}
_pending_submissions: Dict[str, Dict[str, object]] = {}


def submit_plugin(data: Dict[str, object]) -> str:
    submission_id = uuid4().hex
    _pending_submissions[submission_id] = data
    return submission_id


def list_pending(user=Depends(require_role("admin"))) -> List[Dict[str, object]]:
    return [{"id": sid, **data} for sid, data in _pending_submissions.items()]


def approve_submission(submission_id: str, user=Depends(require_role("admin"))):
    if submission_id not in _pending_submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    return _pending_submissions.pop(submission_id)


def reject_submission(submission_id: str, user=Depends(require_role("admin"))):
    if submission_id not in _pending_submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    _pending_submissions.pop(submission_id)
    return {"status": "rejected"}
