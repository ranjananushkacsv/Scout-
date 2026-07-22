"""
api/services/analytics_service.py — lightweight, file-backed log of every
assistant interaction, used to compute the "Impact" numbers on the
dashboard (time/cost saved vs. a human doing the same lookup or escalation
by hand). Same append-only JSON pattern as email_service's escalation log —
no database, just a running record so the numbers are real usage, not
made up.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

_STORE_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "interactions.json"
_STORE_LOCK = Lock()


def _ensure_store():
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE_PATH.exists():
        _STORE_PATH.write_text("[]", encoding="utf-8")


def log_interaction(query: str, blocked: bool, block_reason: Optional[str], tool_calls: list[str]):
    """Record one /api/chat call. Call this once the answer is known — never
    raises, since a logging failure should never break the chat response."""
    try:
        _ensure_store()
        record = {
            "id": uuid.uuid4().hex[:12],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "blocked": blocked,
            "block_reason": block_reason,
            "tool_calls": tool_calls,
        }
        with _STORE_LOCK:
            records = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
            records.append(record)
            _STORE_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    except Exception:
        pass


def _load() -> list:
    _ensure_store()
    with _STORE_LOCK:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))


def get_impact_summary(escalations_handled: int = 0) -> dict:
    records = _load()

    queries_handled = len(records)
    automated_lookups = sum(1 for r in records if r["tool_calls"] and not r["blocked"])
    guardrail_catches = sum(1 for r in records if r["blocked"])

    minutes_saved = (
        automated_lookups * config.MINUTES_SAVED_PER_LOOKUP
        + escalations_handled * config.MINUTES_SAVED_PER_ESCALATION
    )
    hours_saved = round(minutes_saved / 60, 1)
    cost_saved_usd = round(hours_saved * config.HOURLY_LABOR_RATE_USD, 2)

    return {
        "queries_handled": queries_handled,
        "automated_lookups": automated_lookups,
        "escalations_handled": escalations_handled,
        "guardrail_catches": guardrail_catches,
        "minutes_saved": minutes_saved,
        "hours_saved": hours_saved,
        "cost_saved_usd": cost_saved_usd,
        "assumptions": {
            "minutes_per_lookup": config.MINUTES_SAVED_PER_LOOKUP,
            "minutes_per_escalation": config.MINUTES_SAVED_PER_ESCALATION,
            "hourly_labor_rate_usd": config.HOURLY_LABOR_RATE_USD,
        },
    }
