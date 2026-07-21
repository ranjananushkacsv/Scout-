"""
guardrails/patterns.py — regex and keyword patterns used across the
guardrails layer. Kept separate from logic so they're easy to extend
without touching the checking code.
"""

import re

# ---------------------------------------------------------------------------
# PII detection (simple, deliberately conservative — false positives are
# cheaper than a leak)
# ---------------------------------------------------------------------------
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ssn_like": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}

# ---------------------------------------------------------------------------
# Prompt injection — phrases commonly used to try to override system
# instructions, whether coming from user input or (in a real deployment)
# from retrieved/untrusted document content.
# ---------------------------------------------------------------------------
INJECTION_PHRASES = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore the above",
    "disregard previous instructions",
    "disregard the above",
    "you are now",
    "new instructions:",
    "system prompt:",
    "reveal your system prompt",
    "act as if",
    "pretend you are",
    "override your instructions",
    "forget everything above",
    "your new rule is",
]

# ---------------------------------------------------------------------------
# Escalation — requests for actions the assistant must NOT perform itself.
# These are deterministic keyword triggers, intentionally not left to the
# LLM's judgment, because a write-action slipping through is a much worse
# failure than an over-cautious escalation.
# ---------------------------------------------------------------------------
ESCALATION_PHRASES = [
    "approve the refund",
    "approve a refund",
    "process the refund",
    "issue a refund",
    "cancel the order",
    "cancel my order",
    "cancel this order",
    "delete the",
    "remove the inventory",
    "modify the inventory",
    "edit the inventory",
    "update the inventory count",
    "override the",
    "authorize",
    "waive the fee",
    "waive the restocking fee",
    "terminate the contract",
    "approve this",
    "confirm the cancellation",
]

# ---------------------------------------------------------------------------
# Creative-format requests — blocked regardless of subject matter. Even if
# someone asks for a poem/song/story ABOUT logistics, the assistant's scope
# is operational assistance, not creative writing. These are checked as
# standalone words (not exact phrases) so paraphrasing ("make a poem",
# "write a poem", "compose a poem", "poem about X") can't slip through the
# way an exact-phrase list can.
# ---------------------------------------------------------------------------
CREATIVE_FORMAT_KEYWORDS = [
    "poem", "poetry", "haiku", "sonnet", "limerick",
    "song", "lyrics", "rap", "verse",
    "joke", "riddle",
    "story", "short story", "screenplay", "novel", "fairy tale",
]

# ---------------------------------------------------------------------------
# Off-topic quick-reject list — obviously unrelated request types that
# don't need a full LLM classification call. This is a fast first pass;
# anything not caught here goes to the LLM-based topic classifier.
# ---------------------------------------------------------------------------
OBVIOUSLY_OFF_TOPIC_HINTS = [
    "write a poem", "write me a poem", "write a song", "tell me a joke",
    "who is the president", "what's the capital of", "what is the capital of",
    "recipe for", "how do i code", "write a python script", "translate this",
    "what's the weather", "who won the", "movie recommendation",
]
