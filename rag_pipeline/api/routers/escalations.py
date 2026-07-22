"""
api/routers/escalations.py — the "human approval needed" feed: every email
the AI assistant has drafted (and attempted to send) for requests it could
not act on directly.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter

from api.models import EscalationRecord
from api.services.email_service import list_escalations

router = APIRouter(prefix="/api/escalations", tags=["escalations"])


@router.get("", response_model=list[EscalationRecord])
def get_escalations():
    return list_escalations()
