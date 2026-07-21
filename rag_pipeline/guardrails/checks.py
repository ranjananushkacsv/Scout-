"""
guardrails/checks.py — fast, deterministic checks that don't require an
LLM call. These run on every input/output and are cheap enough to apply
unconditionally.
"""

import re

from guardrails.patterns import (
    PII_PATTERNS,
    INJECTION_PHRASES,
    ESCALATION_PHRASES,
    OBVIOUSLY_OFF_TOPIC_HINTS,
    CREATIVE_FORMAT_KEYWORDS,
)


def _any_word_boundary_match(text, phrases):
    """
    Case-insensitive match where each phrase is matched on word boundaries.
    This avoids false positives like "rap" matching inside "wrap" or
    "bubble wrap roll" — a real risk with plain substring checks once you
    have single-word triggers.
    """
    lowered = text.lower()
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
        if re.search(pattern, lowered):
            return True
    return False


def detect_pii(text):
    """
    Scan `text` for likely PII. Returns a list of (type, matched_text) pairs.
    Empty list means nothing detected.
    """
    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append((pii_type, match.group()))
    return findings


def redact_pii(text):
    """Replace detected PII with a [REDACTED:type] placeholder."""
    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED:{pii_type}]", redacted)
    return redacted


def detect_prompt_injection(text):
    """
    Returns True if `text` contains phrases commonly used to try to
    override system instructions. Applied to user input, and would also
    be applied to any externally-sourced document content in a real
    deployment (here, our documents are trusted/synthetic, but the check
    is still run defensively).
    """
    return _any_word_boundary_match(text, INJECTION_PHRASES)


def detect_escalation_request(text):
    """
    Returns True if the user is asking for a write/modify action the
    assistant is not authorized to perform (refund approval, order
    cancellation, inventory edits, etc.). This check is deliberately
    keyword-based and runs BEFORE the LLM sees the query, so escalation
    doesn't depend on the model choosing to follow its instructions.
    """
    return _any_word_boundary_match(text, ESCALATION_PHRASES)


def detect_creative_request(text):
    """
    Returns True if the user is asking for creative-format content (a
    poem, song, story, joke, etc.) REGARDLESS of subject matter. Even a
    poem about inventory or logistics is still out of scope — the
    assistant's job is operational assistance, not creative writing.

    Word-boundary matched so single-word triggers like "rap" don't
    false-positive on "wrap" (e.g. "bubble wrap roll" in the inventory
    data) or "verse" on "universe".
    """
    return _any_word_boundary_match(text, CREATIVE_FORMAT_KEYWORDS)


def quick_off_topic_hint(text):
    """
    Fast keyword pass for obviously off-domain requests. Returns True if
    matched. This is NOT the final word on topic relevance — anything not
    caught here is passed to the LLM-based classifier for a real judgment.
    """
    return _any_word_boundary_match(text, OBVIOUSLY_OFF_TOPIC_HINTS)
