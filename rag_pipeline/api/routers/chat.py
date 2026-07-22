"""
api/routers/chat.py — the AI Assistant endpoint. Wraps the existing
GuardrailedAgent (input guardrails -> LangGraph agent w/ RAG + tools ->
output guardrails) behind a simple session-based HTTP API, and hooks in
escalation-to-email: whenever a request needs a human decision, an email is
drafted and (if SMTP is configured) sent to the ops team.
"""

import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter

from api.models import ChatRequest, ChatResponse, EscalationRecord
from api.services import analytics_service
from api.services.email_service import draft_and_send_escalation

router = APIRouter(prefix="/api/chat", tags=["chat"])

# One shared guardrailed agent (loads the LLM + retriever once), keyed
# per-session message history so multiple browser tabs don't collide.
# Imported lazily inside _get_agent() — the RAG/agent stack (langchain,
# langgraph, sentence-transformers, chromadb) is a heavy optional
# dependency; the dashboard and escalations endpoints must keep working
# even if it isn't installed yet.
_agent = None
_sessions: dict[str, list] = {}

ESCALATION_HINTS = (
    "human escalation",
    "human authorization",
    "requires human",
    "need human approval",
    "not able to approve",
    "escalate this to",
)


def _get_agent():
    global _agent
    if _agent is None:
        from guardrails.pipeline import GuardrailedAgent

        _agent = GuardrailedAgent()
    return _agent


def _looks_like_escalation(answer: str) -> bool:
    lowered = answer.lower()
    return any(hint in lowered for hint in ESCALATION_HINTS)


SOURCE_TAG_RE = re.compile(r"\[Source \d+:\s*([^\]]+)\]")


def _extract_sources(tool_activity: list) -> list[str]:
    """Pull the document/file names cited in search_knowledge_base results,
    in first-seen order, so the frontend can show a clean sources list
    instead of the raw "[Source N: ...]" tags baked into the tool output."""
    from langchain_core.messages import ToolMessage

    seen: dict[str, None] = {}
    for m in tool_activity:
        if not (isinstance(m, ToolMessage) and getattr(m, "name", None) == "search_knowledge_base"):
            continue
        content = m.content if isinstance(m.content, str) else str(m.content)
        for match in SOURCE_TAG_RE.findall(content):
            seen.setdefault(match.strip(), None)
    return list(seen.keys())


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    history = _sessions.get(req.session_id)

    try:
        agent = _get_agent()
        result = agent.ask(req.message, history=history)
    except Exception as exc:
        return ChatResponse(
            session_id=req.session_id,
            answer=(
                "I can't reach my reasoning engine right now (the local LLM "
                "server may be offline). Please make sure Ollama is running "
                "and try again."
            ),
            blocked=False,
            error=str(exc),
        )

    _sessions[req.session_id] = result["new_history"]

    from langchain_core.messages import AIMessage

    tool_activity = result.get("tool_activity", [])

    tool_calls = []
    for m in tool_activity:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            tool_calls.extend(tc["name"] for tc in m.tool_calls)

    sources = _extract_sources(tool_activity)

    escalation = None
    needs_escalation = (
        result["blocked"] and result["block_reason"] == "escalation_request"
    ) or (not result["blocked"] and _looks_like_escalation(result["answer"]))

    if needs_escalation:
        reason = result["block_reason"] or "agent_declined_write_action"
        record = draft_and_send_escalation(req.message, reason)
        escalation = EscalationRecord(**record)

    analytics_service.log_interaction(
        query=req.message,
        blocked=result["blocked"],
        block_reason=result["block_reason"],
        tool_calls=tool_calls,
    )

    return ChatResponse(
        session_id=req.session_id,
        answer=result["answer"],
        blocked=result["blocked"],
        block_reason=result["block_reason"],
        pii_redacted=result["pii_redacted"],
        grounding_ok=result["grounding_ok"],
        tool_calls=tool_calls,
        sources=sources,
        escalation=escalation,
    )


@router.post("/reset")
def reset_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"ok": True}
