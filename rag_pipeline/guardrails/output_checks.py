"""
guardrails/output_checks.py — checks applied to the assistant's final
answer before it's shown to the user.
"""

import re

from guardrails.checks import detect_pii, redact_pii


def check_and_redact_pii(answer_text):
    """
    Scan the outgoing answer for PII. Returns (clean_text, findings).
    If findings is non-empty, clean_text has redactions applied.
    """
    findings = detect_pii(answer_text)
    if not findings:
        return answer_text, []
    return redact_pii(answer_text), findings


def check_grounding(answer_text, tool_was_called):
    """
    Lightweight grounding heuristic: if the answer contains a number that
    looks like a fact (dollar amount, quantity, SKU/order ID pattern) but
    NO tool was called during this turn, flag it as potentially
    ungrounded — the model may be guessing rather than citing retrieved
    data. This is a heuristic, not a proof, so it produces a warning
    rather than blocking the response.

    Returns True if grounding looks fine, False if it looks suspicious.
    """
    looks_factual = bool(
        re.search(r"\$\d|\bSKU-\d|\bORD-\d|\bSHP-\d|\d+%|\d+\s?(kg|days|units|cases)", answer_text)
    )
    if looks_factual and not tool_was_called:
        return False
    return True
