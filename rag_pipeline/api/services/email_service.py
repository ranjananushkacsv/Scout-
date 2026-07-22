"""
api/services/email_service.py — when the guardrailed agent decides a
request needs a human (approve a refund, cancel an order, override a
record, ...), this drafts a notification email for the ops team and sends
it over SMTP.

Every attempt is logged to escalations.json (our lightweight "sent
mail" log) regardless of whether the send succeeds, so the dashboard can
always show what was drafted. If SMTP credentials are not configured in
.env, the service runs in dry-run mode: it still drafts and logs the
email, just doesn't attempt delivery, so the rest of the app keeps working
before real credentials are wired up.
"""

import json
import os
import smtplib
import sys
import uuid
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path
from threading import Lock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ESCALATION_RECIPIENT = os.getenv("ESCALATION_RECIPIENT", SMTP_USER)
SENDER_DISPLAY_NAME = os.getenv("SENDER_DISPLAY_NAME", "Scout AI Assistant")

_STORE_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data" / "escalations.json"
_STORE_LOCK = Lock()


def _ensure_store():
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE_PATH.exists():
        _STORE_PATH.write_text("[]", encoding="utf-8")


def _load_store() -> list:
    _ensure_store()
    with _STORE_LOCK:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))


def _append_store(record: dict):
    _ensure_store()
    with _STORE_LOCK:
        records = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
        records.append(record)
        _STORE_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def list_escalations() -> list:
    return sorted(_load_store(), key=lambda r: r["timestamp"], reverse=True)


def _draft_with_llm(query: str, reason: str) -> tuple[str, str] | None:
    """Try to have Gemma draft a short, professional escalation email. Returns
    None (never raises) if the local LLM isn't reachable, so the caller can
    fall back to the deterministic template."""
    try:
        from langchain_ollama import ChatOllama
        import config

        llm = ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.3,
            num_ctx=2048,
        )
        prompt = (
            "Draft a short, professional internal email notifying the operations "
            "team that a customer/user request needs human approval because the "
            "AI assistant is not authorized to act on it directly.\n\n"
            f"Reason it was escalated: {reason}\n"
            f'Original request: "{query}"\n\n'
            "Respond in EXACTLY this format, nothing else:\n"
            "SUBJECT: <one line subject>\n"
            "BODY:\n<email body, 3-5 sentences, professional tone, sign off as "
            f'"{SENDER_DISPLAY_NAME}">'
        )
        response = llm.invoke(prompt)
        text = response.content.strip()
        if "SUBJECT:" not in text or "BODY:" not in text:
            return None
        subject = text.split("SUBJECT:")[1].split("BODY:")[0].strip()
        body = text.split("BODY:")[1].strip()
        if not subject or not body:
            return None
        return subject, body
    except Exception:
        return None


def _draft_template(query: str, reason: str) -> tuple[str, str]:
    subject = f"[Scout] Human approval needed — {reason.replace('_', ' ')}"
    body = (
        f"Hi team,\n\n"
        f"Scout's AI assistant received a request it is not authorized to act on "
        f"directly and needs a human to review and approve it.\n\n"
        f'Request: "{query}"\n'
        f"Escalation reason: {reason.replace('_', ' ')}\n"
        f"Received: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Please review and action as appropriate.\n\n"
        f"— {SENDER_DISPLAY_NAME}"
    )
    return subject, body


def _send(subject: str, body: str, to_addr: str) -> tuple[bool, str | None]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "dry_run: SMTP_USER / SMTP_PASSWORD not set in .env"
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{SENDER_DISPLAY_NAME} <{SMTP_USER}>"
        msg["To"] = to_addr
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to_addr], msg.as_string())
        return True, None
    except Exception as exc:
        return False, str(exc)


def draft_and_send_escalation(query: str, reason: str) -> dict:
    """Draft an escalation email for `query` (blocked/flagged for the given
    `reason`), attempt to send it, log the attempt, and return the record."""
    drafted = _draft_with_llm(query, reason)
    if drafted is None:
        drafted = _draft_template(query, reason)
    subject, body = drafted

    to_addr = ESCALATION_RECIPIENT or "unconfigured@example.com"
    sent, error = _send(subject, body, to_addr)

    record = {
        "id": uuid.uuid4().hex[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "reason": reason,
        "to": to_addr,
        "subject": subject,
        "body": body,
        "sent": sent,
        "dry_run": not sent and bool(error and error.startswith("dry_run")),
        "error": error,
    }
    _append_store(record)
    return record
