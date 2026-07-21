"""
guardrails/pipeline.py — wraps the LangGraph agent with input and output
guardrails. This is the "safe" entrypoint the CLI/app should call instead
of calling the raw agent directly.

Flow per query:
    1. Input guardrails (fast, no LLM call):
       - prompt injection check
       - escalation-request check (deterministic keyword match)
    2. Input guardrail (LLM call, only if step 1 didn't already decide):
       - topic relevance classification
    3. If all input checks pass -> run the agent (RAG + tools)
    4. Output guardrails:
       - PII redaction
       - grounding heuristic (warns if answer looks factual but no tool ran)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from agent.graph import build_agent, AGENT_SYSTEM_PROMPT
from guardrails.checks import (
    detect_prompt_injection,
    detect_escalation_request,
    detect_creative_request,
    quick_off_topic_hint,
)
from guardrails.classifier import TopicClassifier
from guardrails.output_checks import check_and_redact_pii, check_grounding

ESCALATION_MESSAGE = (
    "That action requires human authorization — I'm not able to approve, "
    "cancel, modify, or override records directly. I can look up the "
    "relevant status or policy for you, and prepare the details for the "
    "right team to action. Would you like me to do that instead?"
)

OFF_TOPIC_MESSAGE = (
    "I'm a logistics and warehousing operations assistant, so I can only "
    "help with questions about shipping, inventory, orders, warehouse "
    "procedures, and related policies. Is there something in that area I "
    "can help you with?"
)

CREATIVE_REQUEST_MESSAGE = (
    "I'm scoped to operational logistics support, not creative writing — "
    "so I won't write poems, songs, stories, or similar content, even on "
    "a logistics topic. I can help you look up inventory, shipment "
    "status, or policy information instead."
)

INJECTION_BLOCKED_MESSAGE = (
    "I can't follow instructions embedded in a message like that. If you "
    "have a genuine logistics or warehousing question, I'm happy to help "
    "with it directly."
)


class GuardrailedAgent:
    def __init__(self):
        self.agent = build_agent()
        self.topic_classifier = TopicClassifier()

    def ask(self, query, history=None):
        """
        Run the full guarded pipeline for a single query.

        `history` is the running list of LangChain messages for multi-turn
        context (same pattern as the plain agent_cli). Pass None to start
        a fresh conversation.

        Returns a dict:
            {
                "answer": str,
                "blocked": bool,          # True if an input guardrail stopped it
                "block_reason": str|None,
                "pii_redacted": bool,
                "grounding_ok": bool,
                "new_history": [...],     # updated message history to carry forward
            }
        """
        history = history or [SystemMessage(content=AGENT_SYSTEM_PROMPT)]

        # --- Input guardrails -------------------------------------------------
        if detect_prompt_injection(query):
            return self._blocked_result(query, history, INJECTION_BLOCKED_MESSAGE, "prompt_injection")

        if detect_escalation_request(query):
            return self._blocked_result(query, history, ESCALATION_MESSAGE, "escalation_request")

        if detect_creative_request(query):
            return self._blocked_result(query, history, CREATIVE_REQUEST_MESSAGE, "creative_request")

        if quick_off_topic_hint(query):
            return self._blocked_result(query, history, OFF_TOPIC_MESSAGE, "off_topic_keyword")

        if not self.topic_classifier.is_relevant(query):
            return self._blocked_result(query, history, OFF_TOPIC_MESSAGE, "off_topic_classifier")

        # --- Run the agent (RAG + tools) --------------------------------------
        history = history + [HumanMessage(content=query)]
        result = self.agent.invoke({"messages": history})
        new_messages = result["messages"]

        tool_was_called = any(isinstance(m, ToolMessage) for m in new_messages)
        final_message = new_messages[-1]
        answer_text = final_message.content

        # --- Output guardrails --------------------------------------------------
        clean_answer, pii_findings = check_and_redact_pii(answer_text)
        grounding_ok = check_grounding(clean_answer, tool_was_called)

        return {
            "answer": clean_answer,
            "blocked": False,
            "block_reason": None,
            "pii_redacted": bool(pii_findings),
            "grounding_ok": grounding_ok,
            "new_history": new_messages,
            "tool_activity": new_messages,  # caller can inspect for tool calls/results
        }

    def _blocked_result(self, query, history, message, reason):
        # Blocked queries are NOT appended to the LLM-facing history — the
        # model never saw them, so there's nothing to carry forward except
        # the conversation continuing from where it was.
        return {
            "answer": message,
            "blocked": True,
            "block_reason": reason,
            "pii_redacted": False,
            "grounding_ok": True,
            "new_history": history,
            "tool_activity": [],
        }
