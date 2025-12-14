from __future__ import annotations
from fastapi import APIRouter

router = APIRouter()

@router.get("/galaxy/health")
def health():
    return {"status": "ok"}
